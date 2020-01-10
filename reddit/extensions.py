from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


bcrypt = Bcrypt()
cors = CORS()
migrate = Migrate()
db = SQLAlchemy()

# Custom extensions
from reddit.search.models import Comment, Thread
from reddit.search.extension import ElasticsearchSql

elasticsearch = ElasticsearchSql()

from reddit.threads.models import Comment as CommentSql, Thread as ThreadSql

elasticsearch.register_sql_model(CommentSql, Comment)
elasticsearch.register_sql_model(ThreadSql, Thread)
