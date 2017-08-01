import logging
from flask import request, jsonify
import string
from sklearn.decomposition import PCA

from server import app, base_dir
from request import form_fields_required
from models import get_model

logger = logging.getLogger(__name__)


@app.route('/embeddings/2d.json', methods=['POST'])
@form_fields_required('words[]', 'model')
def embeddings_2d():
    word_vectors = get_model(request.form['model'])
    words = request.form.getlist('words[]')

    # Remove words that are not in model vocab
    to_be_removed = []
    for word in words:
        try:
            # remove punctuation
            word = "".join(l for l in word if l not in string.punctuation)
            word_vectors[word]
        except KeyError:
            to_be_removed.append(word)
    for word in to_be_removed:
        words.remove(word)

    # reduce to a 2d representation for charting purposes
    embeddings = [word_vectors[word] for word in words]
    pca = PCA(n_components=2)
    two_d_embeddings = pca.fit_transform(embeddings).tolist()

    data = []
    for i in range(len(words)):
        data.append({'word': words[i], 'x': two_d_embeddings[i][0], 'y': two_d_embeddings[i][1]})

    return jsonify({'results': data})
