import os
import urllib

MODEL_GOOGLE_NEWS_URL = "https://dl.dropboxusercontent.com/u/466924777/GoogleNews-vectors-negative300.bin"

embeddings_file_path = os.path.join('./models', 'GoogleNews-vectors-negative300.bin')

if not os.path.isfile(embeddings_file_path):
    print "Google word2vec model not found, downloading file..."
    urllib.urlretrieve(MODEL_GOOGLE_NEWS_URL, embeddings_file_path)
    print "  done!"
else:
    print "Google word2vec model already exists."
