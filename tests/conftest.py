"""Defines fixtures available to all tests."""

import pytest

from reddit.app import create_app
from reddit.extensions import db
from reddit import subreddits, threads, user, votes


@pytest.fixture(scope='module')
def test_client():
    from dotenv import load_dotenv

    load_dotenv('.env_test')

    app = create_app()
    test_client = app.test_client()
    ctx = app.app_context()
    ctx.push()

    yield test_client

    ctx.pop()


@pytest.fixture(scope="module")
def test_database():
    db.drop_all()
    db.create_all()

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
        author_id=user1.id
    )

    data = {'users': [user1, user2],
            'subreddits': [sub1],
            'threads': [thread1]}

    for key, models in data.items():
        for instance in models:
            instance.save()

    yield db, data

    for key, models in data.items():
        for instance in models:
            instance.delete()

    db.drop_all()
