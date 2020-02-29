from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


bcrypt = Bcrypt()
cors = CORS()
migrate = Migrate()
db = SQLAlchemy()


# Custom extensions
from reddit.cache import ObjectCache, ListCache
from reddit.elasticsearch import ElasticsearchSql
from reddit.events import EventPublisher

cache = ObjectCache('object')
list_cache = ListCache('list')
elasticsearch = ElasticsearchSql()
event_publisher = EventPublisher()
