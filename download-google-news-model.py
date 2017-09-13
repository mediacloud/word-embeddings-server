import os
import urllib

# this is hosted in Rahul's MIT Dropbox folder
MODEL_GOOGLE_NEWS_URL = "https://www.dropbox.com/s/ube0ajo5jej8g62/GoogleNews-vectors-negative300.bin?dl=0"

model_dir = "./models"
model_name = "GoogleNews-vectors-negative300.bin"

model_file_name = os.path.join(model_dir, model_name)

if not os.path.exists(model_dir):
    os.mkdir(model_dir)

if not os.path.isfile(model_file_name):
    print "Google word2vec model not found, downloading model file from the cloud..."
    urllib.urlretrieve(MODEL_GOOGLE_NEWS_URL, model_file_name)
    print "  done!"
else:
    print "Google word2vec model already exists."
