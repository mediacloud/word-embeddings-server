import logging
import os
import gensim

from server import base_dir

MODEL_GOOGLE_NEWS = "GoogleNews-vectors-negative300.bin"

logger = logging.getLogger(__name__)

model_cache = {}  # keyed by model name


class UnknownModelException(Exception):
    pass


def get_model(name):
    if name == MODEL_GOOGLE_NEWS:
        return _load_model(MODEL_GOOGLE_NEWS)
    raise UnknownModelException(name)


def _load_model(name):
    if name not in model_cache:
        logger.info("Loading pre-trained word to vec model named {}...".format(name))
        path_to_model = _path_to_model(name)
        model = gensim.models.keyedvectors.KeyedVectors.load_word2vec_format(path_to_model, binary=True)
        logger.info("  loaded")
        model_cache[name] = model
    return model_cache[name]


def _path_to_model(name):
    return os.path.join(base_dir, 'models', name)
