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
settings = None # on deployed instance these will be ENV_VARS
server_config_file_path = os.path.join(base_dir, 'config', 'server.config')
if os.path.exists(server_config_file_path):
    settings = ConfigParser.ConfigParser()
    settings.read(server_config_file_path)
else:
    logging.warn("no settings!")
    # TODO: load from environment variables

# Set up some logging
try:
    entry = Sentry(dsn=settings.get('sentry', 'dsn'))
    handler = SentryHandler(settings.get('sentry', 'dsn'))
    setup_logging(handler)
except Exception:
    logging.info("no sentry logging")

with open(os.path.join(base_dir, 'config', 'logging.json'), 'r') as f:
    logging_config = json.load(f)
    logging_config['handlers']['file']['filename'] = os.path.join(base_dir, logging_config['handlers']['file']['filename'])
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)
logger.info("---------------------------------------------------------------------------")

def create_app():
    # Factory method to create the app
    my_app = Flask(__name__)
    return my_app

app = create_app()
app.secret_key = settings.get('server', 'secret_key')

# prefill the google news model for deterministic query times once server has started
import server.models
logger.info("Pre-loading GoogleNews model...")
models.get_model(models.MODEL_GOOGLE_NEWS)
logger.info("  done - ready for requests!")

# now load in the appropriate view endpoints, after the app has been initialized
import server.views
