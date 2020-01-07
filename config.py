import os


class Base:
    SQLALCHEMY_DATABASE_URI = os.getenv("APP_DATABASE_URI")
    SECRET_KEY = os.getenv("APP_SECRET_KEY", "super-secret")
    DEBUG = False


class Development(Base):
    SQLALCHEMY_DATABASE_URI = os.getenv("APP_DATABASE_URI", "sqlite:///reddit.db")
    DEBUG = True


class Production(Base):
    pass


class Testing(Base):
    SQLALCHEMY_DATABASE_URI = os.getenv('APP_DATABASE_URI', 'sqlite:///test.db')
    DEBUG = True
