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
    name = _topic_model_cache_name(topics_id, snapshots_id)
    if name not in model_cache:
        # not in memory, but might be on disk
        file_path = os.path.join(base_dir, MODEL_DIR, name)
        if os.path.exists(file_path):
            model_cache[name] = gensim.models.keyedvectors.KeyedVectors.load(file_path)
            return True
        return False
    return True


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
        snapshot = [s for s in all_snapshots if s['snapshots_id'] == int(snapshots_id)][0]
        if len(snapshot['word2vec_models']) is 0:
            # there no snapshots for this model
            return None
        model_info = snapshot['word2vec_models'][0]
        raw_model = mc.topicSnapshotWord2VecModel(topics_id, snapshots_id, model_info['models_id'])
        _cache_topic_model(topics_id, snapshots_id, raw_model)
    return _get_cached_model(topics_id, snapshots_id)


def _load_model_from_file(name):
    if name not in model_cache:
        logger.info("Loading pre-trained word to vec model named {}...".format(name))
        path_to_model = _path_to_model(name)
        if name.endswith('.bin'):  # the google one was trained in C and saved as a binary
            model = gensim.models.keyedvectors.KeyedVectors.load_word2vec_format(path_to_model, binary=True)
        else:  # our models are saved with a call to save, so use `load` to load them
            model = gensim.models.keyedvectors.KeyedVectors.load(path_to_model)
        logger.info("  loaded")
        model_cache[name] = model
    return model_cache[name]


def _path_to_model(name):
    return os.path.join(base_dir, MODEL_DIR, name)
