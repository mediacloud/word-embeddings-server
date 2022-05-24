import logging
import os

import gensim

from server import base_dir, mc

MODEL_DIR = "models"

GOOGLE_NEWS_MODEL_FILENAME = "GoogleNews-vectors-negative300.bin"

logger = logging.getLogger(__name__)

model_cache = {}  # keyed by model name

google_model = None


def get_google_news_model():
    global google_model
    if google_model is None:
        model_filename = GOOGLE_NEWS_MODEL_FILENAME
        google_model = _load_model_from_file(model_filename)
    return google_model


def _topic_model_cache_name(topics_id, snapshots_id):
    return "topic-{}-snapshot-{}".format(topics_id, snapshots_id)


def _is_topic_model_cached(topics_id, snapshots_id):
    # this tries to be smart about checking for it in memory, or from the directory if it is'nt in memory already
    name = _topic_model_cache_name(topics_id, snapshots_id)
    if name not in model_cache:
        # not in memory, but might be on disk
        file_path = os.path.join(base_dir, MODEL_DIR, name)
        if os.path.exists(file_path):
            # if the file exists, make sure it isn't in an old format (which throws an Attribute error about not
            # having EuclideanKeyedVectors)
            try:
                model_cache[name] = gensim.models.keyedvectors.KeyedVectors.load_word2vec_format(file_path, binary=True)
            except Exception as ex:
                logger.warning("Unable to load model into cache from {}: {}".format(file_path, str(ex)))
                _remove_topic_model(file_path)
                # let the requester try and fetch the model again, cause we don't have a good version of it
                return False
            # found it on disk and loaded it into memory
            return True
        # not in memory and not on disk
        return False
    # exists in model cache in memory
    return True


def _remove_topic_model(file_path):
    os.remove(file_path)


def _cache_topic_model(topics_id, snapshots_id, model):
    name = _topic_model_cache_name(topics_id, snapshots_id)
    # and write it to disk here too
    model_byte_array = bytearray(model)
    model_name = _topic_model_cache_name(topics_id, snapshots_id)
    path_to_model = os.path.join(base_dir, MODEL_DIR, model_name)
    cache_file = open(path_to_model, 'w')
    cache_file.write(model_byte_array)
    cache_file.close()
    # load it into memory
    model_cache[name] = _load_model_from_file(model_name)


def _get_cached_model(topics_id, snapshots_id):
    name = _topic_model_cache_name(topics_id, snapshots_id)
    return model_cache[name]


def get_topic_model(topics_id=None, snapshots_id=None):
    if not _is_topic_model_cached(topics_id, snapshots_id):
        all_snapshots = mc.topicSnapshotList(topics_id)
        if len(all_snapshots) == 0:
            raise RuntimeError('No snapshots for topic {}'.format(topics_id))
        snapshot = [s for s in all_snapshots if s['snapshots_id'] == int(snapshots_id)]
        if len(snapshot) == 0:
            raise RuntimeError('No snapshot {} in topic {}'.format(snapshots_id, topics_id))
        snapshot = snapshot[0]
        if len(snapshot['word2vec_models']) == 0:
            raise RuntimeError('No word2ve models for topic {}/{}'.format(topics_id, snapshots_id))
        model_info = snapshot['word2vec_models'][0]
        raw_model = mc.topicSnapshotWord2VecModel(topics_id, snapshots_id, model_info['models_id'])
        _cache_topic_model(topics_id, snapshots_id, raw_model)
    return _get_cached_model(topics_id, snapshots_id)


def _load_model_from_file(name):
    if name not in model_cache:
        logger.info("Loading pre-trained word to vec model named {}...".format(name))
        path_to_model = _path_to_model(name)
        try:
            # The google news ones is in this C-style binary format, as are the ones we generate
            model = gensim.models.keyedvectors.KeyedVectors.load_word2vec_format(path_to_model, binary=True)
        except Exception as ex:
            logger.warning("Unable to load model {}".format(name))
            raise ex
        logger.info("  loaded")
        model_cache[name] = model
    return model_cache[name]


def _path_to_model(name):
    return os.path.join(base_dir, MODEL_DIR, name)
