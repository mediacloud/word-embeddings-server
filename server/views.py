import logging
from flask import request, jsonify
import string
from sklearn.decomposition import PCA

from server import app
from request import form_fields_required
from models import get_model

logger = logging.getLogger(__name__)


@app.route('/embeddings/2d.json', methods=['POST'])
@form_fields_required('words[]', 'model')
def embeddings_2d():
    word_vectors = get_model(request.form['model'])
    words = request.form.getlist('words[]')

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
    two_d_embeddings = pca.fit_transform(embeddings).tolist()
    words_with_model_info = []
    for i in range(len(words_in_model)):
        words_with_model_info.append({'word': words_in_model[i]['word'], 'x': two_d_embeddings[i][0], 'y': two_d_embeddings[i][1]})

    results = []
    for word in words:
        word_model_data = next(iter([w for w in words_with_model_info if w["word"] == word]), None)
        if word_model_data:
            results.append({'word': word, 'x': word_model_data['x'], 'y': word_model_data['y']})
        else:
            results.append({'word': word, 'x': None, 'y': None})

    return jsonify({'results': results})
