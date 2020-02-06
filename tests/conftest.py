"""Defines fixtures available to all tests."""
import os
import pathlib
import pytest

from flask import current_app
from reddit.app import create_app
from reddit.extensions import db
from reddit import subreddits, threads, user, votes


@pytest.fixture(scope='session')
def test_client(request):
    os.environ['FLASK_ENV'] = 'testing'

    app = create_app()
    test_client = app.test_client()
    ctx = app.app_context()
    ctx.push()

    request.addfinalizer(lambda: ctx.pop())

    yield test_client


@pytest.fixture(scope="session")
def test_database(request, test_client):
    db.create_all()

    def tear_down():
        db.drop_all()
        # Hack for sqlite always placing database in app directory rather than root
        database_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
        if database_uri.startswith('sqlite'):
            db_path = database_uri.strip('sqlite:///')
            db_name = pathlib.Path(db_path).name
            for dirname, _, filenames in os.walk('.'):
                for filename in filenames:
                    if filename == db_name:
                        os.remove(os.path.join(dirname, filename))
                        return

    request.addfinalizer(tear_down)

    yield db


@pytest.fixture(scope='module')
def test_data(test_database):
    user1 = user.models.User(username='user_test1', email='test1@gmail.com', password='password')
    user2 = user.models.User(username='user_test2', email='test2@gmail.com', password='password')
    user1.save()
    user2.save()

    sub1 = subreddits.models.Subreddit(
        name='test_sub1',
        description='A subreddit for testing.',
        creator_id=user1.id
    )

    thread1 = threads.models.Thread(
        title='test_thread',
        description='A thread for testing',
        author_id=user1.id,
        subreddit=sub1
    )

    data = {'users': [user1, user2],
            'subreddits': [sub1],
            'threads': [thread1]}

    for key, models in data.items():
        for instance in models:
            instance.save()

    yield data

    for key, models in data.items():
        for instance in models:
            instance.delete()
