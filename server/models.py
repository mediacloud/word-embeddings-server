import logging
import os
import gensim

from server import base_dir

MODEL_DIR = "models"

MODEL_GOOGLE_NEWS = "GoogleNews-vectors-negative300.bin"
MODEL_GOOGLE_NEWS_SHORTNAME = "GoogleNews-vectors-negative300"

logger = logging.getLogger(__name__)

model_cache = {}  # keyed by model name


def model_name_list():
    all_files = [f for f in os.listdir(MODEL_DIR) if not f.startswith('.')]
    files = []
    for f in all_files:
        if '.' in f:
            files.append(f[:f.index('.')])
        else:
            files.append(f)
    return list(set(files))


class UnknownModelException(Exception):
    pass


def get_model(name):
    if name == MODEL_GOOGLE_NEWS_SHORTNAME:
        return _load_model(MODEL_GOOGLE_NEWS)
    if name in model_name_list():
        return _load_model(name)
    raise UnknownModelException(name)


def _load_model(name):
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
