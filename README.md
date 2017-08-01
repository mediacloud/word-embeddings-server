Media Cloud Word Embeddings Server
==================================

A micro-service to support analyzing words based on word embeedings (ala word2vec).

Dev Installation
----------------

Python 2.7:
 * python 2.7 https://www.python.org/download/releases/2.7/
 * `pip install virtualenv` (if necessary) [also install/link pip if you don't have it (if on Mac OS, use sudo easy_install pip)]
 * [`virtualenv venv`](https://virtualenv.pypa.io/en/stable/)
 * activate your virtualenv (OSX: `source venv/bin/activate`, Windows: `call venv\Scripts\activate`) to activate your virtual environment (and not run any global python installations)
 * On Window, make sure to create an environment variable: `set NODE_ENV=dev`
 * in MediaMeter directory run `pip install -r requirements.txt` 
 
Developing
----------

We develop [with PyCharm](https://www.jetbrains.com/pycharm/).

Running
-------

`python run.py`

Deplying
--------

This is configured to deploy with docker.
