from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


bcrypt = Bcrypt()
cors = CORS()
migrate = Migrate()
db = SQLAlchemy()

import redis

cache = redis.Redis(host='localhost', port='6379')

# Custom extensions
from reddit.elasticsearch import ElasticsearchSql
from reddit.events import EventProcessor

elasticsearch = ElasticsearchSql()
event_processor = EventProcessor()
