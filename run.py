import os
import logging

from werkzeug.serving import run_simple
from dotenv import load_dotenv

# when developing locally we keep env-vars in a `.env` file
basedir = os.path.abspath(os.path.dirname(__file__))
# load env-vars from .env file if there is one
test_env = os.path.join(basedir, '.env')
if os.path.isfile(test_env):
    load_dotenv(dotenv_path=os.path.join(basedir, '.env'), verbose=True)

from server import app

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    run_simple('localhost', 8001, app, use_reloader=True, use_debugger=True)
