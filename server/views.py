import logging
from flask import request, jsonify, render_template
import string
from sklearn.decomposition import PCA

from server import app, VERSION
from request import form_fields_required
from models import get_model, model_name_list

logger = logging.getLogger(__name__)


@app.route('/', methods=['GET'])
def model_list():
    model_names = model_name_list()
    return render_template('index.html', models=model_names)


@app.route('/models.json', methods=['GET'])
def model_list_json():
    model_names = model_name_list()
    return jsonify(model_names)


@app.route('/embeddings/2d.json', methods=['POST'])
@form_fields_required('words[]', 'model')
def embeddings_2d():
    word_vectors = get_model(request.form['model'])
    words = request.form.getlist('words[]')
    words = [w for w in words if len(w) > 0]    # do a little extra cleanup - no empty words

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

    return jsonify({
        'results': results,
        'version': VERSION
    })


@app.route('/embeddings/<word>/similar-words.json', methods=['GET'])
def embeddings_similar_words(word):
    word_vectors = get_model(request.args.get('model'))
    try:
        similar_words = word_vectors.most_similar(word)
    except KeyError:
        # means the word is not in the vocabulary we are using
        similar_words = []

    results = []
    for sim_word in similar_words:
        results.append({'word': sim_word[0], 'score': sim_word[1]})

    return jsonify({
        'results': results,
        'word': word,
        'version': VERSION
    })
