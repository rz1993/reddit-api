import click
import os
from flask import current_app
from flask.cli import AppGroup, with_appcontext
from reddit.extensions import elasticsearch
from reddit.jobs.comments import CommentConsumer
from reddit.jobs.threads import ThreadConsumer
from reddit.jobs.votes import VoteConsumer


HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)
TEST_PATH = os.path.join(PROJECT_ROOT, 'tests')


@click.command()
def test():
    """Run the tests."""
    import pytest
    rv = pytest.main([TEST_PATH, '--verbose'])
    exit(rv)


@click.command()
def clean():
    """Remove *.pyc and *.pyo files recursively starting at current directory.
    Borrowed from Flask-Script, converted to use Click.
    """
    for dirpath, _, filenames in os.walk('.'):
        for filename in filenames:
            if filename.endswith('.pyc') or filename.endswith('.pyo'):
                full_pathname = os.path.join(dirpath, filename)
                click.echo('Removing {}'.format(full_pathname))
                os.remove(full_pathname)
        if dirpath.endswith('__pycache__'):
            os.rmdir(dirpath)


@click.command()
def create_indexes():
    elasticsearch.create_all()


@click.command()
@click.argument('type')
@with_appcontext
def run_consumer(type):
    if type == "vote":
        cls = VoteConsumer
    elif type == "thread":
        cls = ThreadConsumer
    elif type == "comment":
        cls = CommentConsumer

    consumer = cls(current_app)
    consumer.start()
