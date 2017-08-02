import os
import urllib
from server.models import MODEL_DIR, MODEL_GOOGLE_NEWS

MODEL_GOOGLE_NEWS_URL = "https://dl.dropboxusercontent.com/u/466924777/GoogleNews-vectors-negative300.bin"

emmbedings_file_path = os.path.join(MODEL_DIR, MODEL_GOOGLE_NEWS)

if not os.path.isfile(emmbedings_file_path):
    print "Google word2vec model not found, downloading file..."
    urllib.urlretrieve(MODEL_GOOGLE_NEWS_URL, emmbedings_file_path)
    print "  done!"
