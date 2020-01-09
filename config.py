import os


class Base:
    ITEMS_PER_PAGE          = 20
    SQLALCHEMY_DATABASE_URI = os.getenv("APP_DATABASE_URI")
    SECRET_KEY              = os.getenv("APP_SECRET_KEY", "super-secret")
    DEBUG                   = False

    ES_HOST                 = os.getenv("ES_HOST")
    ES_USER                 = os.getenv("ES_USER")
    ES_PASSWORD             = os.getenv("ES_PASSWORD")


class Development(Base):
    SQLALCHEMY_DATABASE_URI = os.getenv("APP_DATABASE_URI", "sqlite:///reddit.db")
    DEBUG                   = True


class Production(Base):
    pass


class Testing(Base):
    SQLALCHEMY_DATABASE_URI = os.getenv('APP_DATABASE_URI', 'sqlite:///test.db')
    DEBUG                   = True
