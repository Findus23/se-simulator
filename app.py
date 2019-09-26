# Blog configuration values.
import sentry_sdk
from flask import Flask
from playhouse.flask_utils import FlaskDB
from playhouse.pool import PooledMySQLDatabase
from sentry_sdk.integrations.flask import FlaskIntegration

import config

DATABASE = PooledMySQLDatabase("se-simulator", **config.db)

if config.sentryDSN:
    sentry_sdk.init(
        dsn=config.sentryDSN,
        integrations=[FlaskIntegration()]
    )

# Create a Flask WSGI app and configure it using values from the module.
app = Flask(__name__)
app.config.from_object(__name__)

flask_db = FlaskDB(app)

db = flask_db.database
