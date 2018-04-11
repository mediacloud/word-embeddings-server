Media Cloud Word Embeddings Server
==================================

A micro-service to support analyzing words based on models of word embeddings (aka. "word2vec").

Dev Installation
----------------

 * python 2.7 https://www.python.org/download/releases/2.7/
 * `pip install virtualenv` (if necessary) [also install/link pip if you don't have it (if on Mac OS, use sudo easy_install pip)]
 * [`virtualenv venv`](https://virtualenv.pypa.io/en/stable/)
 * activate your virtualenv (and not run any global python installations)
   * on OSX: `source venv/bin/activate`
   * on Windows: `call venv\Scripts\activate`
 * run `pip install -r requirements.txt` to install dependencies
 * run `python download-google-news-model.py` to download the google news model file
 
Developing
----------

We develop [with PyCharm](https://www.jetbrains.com/pycharm/).

Copy the `config/app.config.template` to `config/app.config` and fill in the values.

Running
-------

Two options:
 1. Development: run `python run.py` to test it out  
 2. Production-like: run `./run.sh` to run it with gunicorn

You can then hit the local homepage to try it out from a simple web-testing harness: `http://localhost:8000`

Or you can test that with something like this (the first request takes a while to load the giant model into memory):

```python
import requests
response = requests.post("http://localhost:8000/api/v2/google-news2d.json",
                         data = {'words[]':['apples', 'bananas', 'three']})
print response.json()
```

Deploying
---------

This is configured to deploy as a Heroku buildpack to [dokku](http://dokku.viewdocs.io/dokku/).

You'll need to do something like this to set the required environment variables:

`dokku config:set word-embeddings SECRET_KEY=oiwajj243josadjoi SENTRY_DSN=https://THING1:THING2@sentry.io/THING3 MEDIA_CLOUD_API_KEY=MY_AWESOME_KEY`

Releasing
---------

1. Update the semantic version number in `server/__init.py__`
2. Tag the repository with that number, like `v4.5.2`
3. Push it to the server, like `git push dokku v4.5.2:master`
