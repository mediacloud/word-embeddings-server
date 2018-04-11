import os
import logging.config
import sys
from flask import Flask
from raven.conf import setup_logging
from raven.contrib.flask import Sentry
from raven.handlers.logging import SentryHandler
import mediacloud

from config import get_default_config, ConfigException

VERSION = "2.1.0"

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# just log to stdout so it works well on prod containers
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# load the settings
config = get_default_config()

# just log to stdout so it works well on prod containers
log_level = "WARN"
try:
    log_level = config.get("LOG_LEVEL")
except ConfigException as ce:
    logging.info("No log level set, defaulting to WARN")
logging.basicConfig(stream=sys.stdout, level=log_level)

logger = logging.getLogger(__name__)
logger.info("---------------------------------------------------------------------------")

# create Media Cloud api client for fetching model info and models themselves
mc = mediacloud.api.MediaCloud(config.get("MEDIA_CLOUD_API_KEY"))

# Set up sentry logging service
sentry_dsn = None
try:
    sentry_dsn = config.get("SENTRY_DSN")
except ConfigException as ce:
    logging.warning(ce)
if sentry_dsn and len(sentry_dsn) > 0:
    handler = SentryHandler(sentry_dsn)
    setup_logging(handler)
else:
    logger.info("No sentry logging")


def create_app():
    global sentry_dsn
    # Factory method to create the app
    my_app = Flask(__name__)
    my_app.secret_key = config.get('SECRET_KEY')
    if sentry_dsn and len(sentry_dsn) > 0:
        Sentry(my_app, dsn=sentry_dsn)
    return my_app

app = create_app()

# now load in the appropriate view endpoints, after the app has been initialized
import server.views.website
import server.views.api
