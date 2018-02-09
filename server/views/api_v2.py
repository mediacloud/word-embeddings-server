import string
import logging
from flask import request, jsonify
from sklearn.decomposition import PCA

from server import app, VERSION
from server.request import form_fields_required
from server.models import get_topic_model, get_google_news_model

logger = logging.getLogger(__name__)


@app.route('/api/v2/google-news/2d', methods=['POST'])
@form_fields_required('words[]')
def google_embeddings_2d():
    word_vectors = get_google_news_model()
    words = request.form.getlist('words[]')
    results = _embeddings_2d(word_vectors, words)
    return jsonify({
        'results': results,
        'version': VERSION
    })


@app.route('/api/v2/topics/{topics_id}/snapshots/{snapshots_id}/2d', methods=['POST'])
@form_fields_required('words[]')
def topic_embeddings_2d(topics_id, snapshots_id):
    word_vectors = get_topic_model(topics_id, snapshots_id)
    words = _words_from_form(request.form)
    results = _embeddings_2d(word_vectors, words)
    return jsonify({
        'results': results,
        'version': VERSION
    })


def _words_from_form(request_form):
    words = request_form.getlist('words[]')
    words = [w for w in words if len(w) > 0]
    return words


def _embeddings_2d(word_vectors, words):
    # Remove words that are not in model vocab
    words_in_model = []
    for word in words:
        try:
            # remove punctuation
            cleaned_word = "".join(l for l in word if l not in string.punctuation)
            word_vectors[cleaned_word]
            words_in_model.append({'word': word, 'cleaned_word': cleaned_word})
        except KeyError:
            # ignore words not in model
            pass
    # reduce to a 2d representation for charting purposes
    embeddings = [word_vectors[word] for word in [w['cleaned_word'] for w in words_in_model]]
    pca = PCA(n_components=2)
    try:
        two_d_embeddings = pca.fit_transform(embeddings).tolist()
    except ValueError:
        # means there aren't any input words actually in the model
        two_d_embeddings = []
    words_with_model_info = []
    if len(words_in_model) != len(two_d_embeddings):
        # this is not crazy for a topic model, so just debug log it
        logger.debug("Number of results from model didn't match input length - maybe foreign words?")
    else:
        for i in range(len(words_in_model)):
            words_with_model_info.append({'word': words_in_model[i]['word'], 'x': two_d_embeddings[i][0], 'y': two_d_embeddings[i][1]})
    results = []
    for word in words:
        word_model_data = next(iter([w for w in words_with_model_info if w["word"] == word]), None)
        if word_model_data:
            results.append({'word': word, 'x': word_model_data['x'], 'y': word_model_data['y']})
        else:
            results.append({'word': word, 'x': None, 'y': None})

    return results


@app.route('/api/v2/google-news/similar-words', methods=['POST'])
@form_fields_required('words[]')
def google_similar_words():
    word_vectors = get_google_news_model()
    words = request.form.getlist('words[]')
    results = [{'word': w, 'results': _embeddings_similar_words(word_vectors, w)} for w in words]
    return jsonify({
        'results': results,
        'version': VERSION
    })


@app.route('/api/v2/topics/{topics_id}/snapshots/{snapshots_id}/similar-words', methods=['POST'])
@form_fields_required('words[]')
def topic_similar_words(topics_id, snapshots_id):
    word_vectors = get_topic_model(topics_id, snapshots_id)
    words = request.form.getlist('words[]')
    results = [{'word': w, 'results': _embeddings_similar_words(word_vectors, w)} for w in words]
    return jsonify({
        'results': results,
        'word': words[0],
        'version': VERSION
    })


def _embeddings_similar_words(word_vectors, word):
    try:
        similar_words = word_vectors.most_similar(word)
    except KeyError:
        # means the word is not in the vocabulary we are using
        similar_words = []
    results = []
    for sim_word in similar_words:
        results.append({'word': sim_word[0], 'score': sim_word[1]})
    return results
