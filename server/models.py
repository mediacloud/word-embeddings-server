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
    return name in model_cache


def _cache_topic_model(topics_id, snapshots_id, model):
    name = _topic_model_cache_name(topics_id, snapshots_id)
    model_cache[name] = model


def _get_cached_model(topics_id, snapshots_id):
    name = _topic_model_cache_name(topics_id, snapshots_id)
    return model_cache[name]


def get_topic_model(topics_id=None, snapshots_id=None):
    if not _is_topic_model_cached(topics_id, snapshots_id):
        all_snapshots = mc.topicSnapshotList(topics_id)
        snapshot = [s for s in all_snapshots if s['snapshots_id'] == snapshots_id][0]
        model_info = snapshot['word2vec_models'][0]
        model = mc.topicSnapshotWord2VecModel(topics_id, snapshots_id, model_info['models_id'])
        # TODO: save to file from raw octect stream
        _cache_topic_model(topics_id, snapshots_id, model)
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
