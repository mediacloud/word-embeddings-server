import os
import logging.config
import ConfigParser
import sys
from flask import Flask
from raven.conf import setup_logging
from raven.contrib.flask import Sentry
from raven.handlers.logging import SentryHandler

VERSION = "1.0.0"

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# just log to stdout so it works well on prod containers
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# load the settings
server_config_file_path = os.path.join(base_dir, 'config', 'server.config')
SENTRY_DSN = None
SECRET_KEY = None
LOG_LEVEL = 'WARN'
if os.path.exists(server_config_file_path):
    logging.info("Loading settings from config/server.config")
    settings = ConfigParser.ConfigParser()
    settings.read(server_config_file_path)
    SENTRY_DSN = settings.get('sentry', 'dsn')
    SECRET_KEY = settings.get('server', 'secret_key')
else:
    logging.info("Loading settings from environment variables")
    try:
        SENTRY_DSN = os.environ.get('SENTRY_DSN')   # it would do this by default, but let's be intentional about it
        SECRET_KEY = os.environ.get('SECRET_KEY')
        LOG_LEVEL = os.environ.get('LOG_LEVEL')
    except KeyError:
        logging.error("You need to define the SECRET_KEY environment variable")
        sys.exit(0)

# just log to stdout so it works well on prod containers
logging.basicConfig(stream=sys.stdout, level=LOG_LEVEL)

logger = logging.getLogger(__name__)
logger.info("---------------------------------------------------------------------------")

# Set up sentry logging service
if SENTRY_DSN:
    handler = SentryHandler(SENTRY_DSN)
    setup_logging(handler)
else:
    logging.info("No sentry logging")


def create_app():
    global SENTRY_DSN
    # Factory method to create the app
    my_app = Flask(__name__)
    my_app.secret_key = SECRET_KEY
    if SENTRY_DSN:
        Sentry(my_app, dsn=SENTRY_DSN)
    return my_app

app = create_app()

# now load in the appropriate view endpoints, after the app has been initialized
import server.views
