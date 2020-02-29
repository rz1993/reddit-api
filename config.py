import os
from sqlalchemy.engine.url import URL


def make_database_url():
    db_url = URL(
        'postgresql+psycopg2',
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        username=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        database=os.getenv('POSTGRES_DB')
    )
    return str(db_url)


class Base:
    ITEMS_PER_PAGE          = 20
    SQLALCHEMY_DATABASE_URI = make_database_url()
    SECRET_KEY              = os.getenv("APP_SECRET_KEY", "super-secret")
    DEBUG                   = False

    ES_ENABLED              = False
    ES_HOST                 = os.getenv("ES_HOST")
    ES_USER                 = os.getenv("ES_USER")
    ES_PASSWORD             = os.getenv("ES_PASSWORD")

    OBJECT_CACHE_HOST       = os.getenv("OBJECT_CACHE_HOST")
    OBJECT_CACHE_PORT       = os.getenv("OBJECT_CACHE_PORT")

    LIST_CACHE_HOST         = os.getenv("LIST_CACHE_HOST")
    LIST_CACHE_PORT         = os.getenv("LIST_CACHE_PORT")
    LIST_CACHE_SIZE_LIMIT   = 500

    RABBITMQ_HOST           = os.getenv("RABBITMQ_HOST") #'localhost'
    RABBITMQ_PORT           = os.getenv("RABBITMQ_PORT") #'5672'
    RABBITMQ_EXCHANGE       = os.getenv("RABBITMQ_EXCHANGE", 'reddit_events')
    RABBITMQ_HEARTBEAT      = os.getenv("RABBITMQ_HEARTBEAT", 30)
    RABBITMQ_TIMEOUT        = os.getenv("RABBITMQ_TIMEOUT", 10)


class Development(Base):
    #SQLALCHEMY_DATABASE_URI = make_database_url()
    DEBUG                   = True

    #OBJECT_CACHE_HOST       = os.getenv("OBJECT_CACHE_HOST", "localhost")
    #OBJECT_CACHE_PORT       = os.getenv("OBJECT_CACHE_PORT", "6379")

    #LIST_CACHE_HOST         = os.getenv("LIST_CACHE_HOST", "localhost")
    #LIST_CACHE_PORT         = os.getenv("LIST_CACHE_PORT", "6380")
    #LIST_CACHE_SIZE_LIMIT   = 500

    #RABBITMQ_HOST           = os.getenv("RABBITMQ_HOST", "localhost") #'localhost'
    #RABBITMQ_PORT           = os.getenv("RABBITMQ_PORT", "5672") #'5672'


class Production(Base):
    pass


class Testing(Base):
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    DEBUG                   = True

    ES_HOST                 = None
