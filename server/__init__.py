import os
import logging.config
import ConfigParser
import json
from flask import Flask
from raven.conf import setup_logging
from raven.contrib.flask import Sentry
from raven.handlers.logging import SentryHandler

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# load the settings
server_config_file_path = os.path.join(base_dir, 'config', 'server.config')
SENTRY_DSN = None
SECRET_KEY = None
if os.path.exists(server_config_file_path):
    logging.info("Loading settings from config/server.config")
    settings = ConfigParser.ConfigParser()
    settings.read(server_config_file_path)
    SENTRY_DSN = settings.get('sentry', 'dsn')
    SECRET_KEY = settings.get('server', 'secret_key')
else:
    logging.info("Loading settings from environment variables")
    SENTRY_DSN = os.environ['SENTRY_DSN']
    SECRET_KEY = os.environ['SECRET_KEY']

# Set up some logging
if SENTRY_DSN:
    handler = SentryHandler(SENTRY_DSN)
    setup_logging(handler)
else:
    logging.info("No sentry logging")

with open(os.path.join(base_dir, 'config', 'logging.json'), 'r') as f:
    logging_config = json.load(f)
    logging_config['handlers']['file']['filename'] = os.path.join(base_dir, logging_config['handlers']['file']['filename'])
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)
logger.info("---------------------------------------------------------------------------")


def create_app():
    # Factory method to create the app
    my_app = Flask(__name__)
    my_app.secret_key = SECRET_KEY
    return my_app

app = create_app()

# now load in the appropriate view endpoints, after the app has been initialized
import server.views
