import logging
from flask import render_template

from server import app, VERSION

logger = logging.getLogger(__name__)


@app.route('/', methods=['GET'])
def model_list():
    return render_template('index.html', version=VERSION)
