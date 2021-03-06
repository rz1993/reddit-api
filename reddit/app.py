from flask import Flask, jsonify
from reddit import listing, search, subreddits, threads, user, votes
from reddit import commands
from reddit.errors import InvalidUsage
from reddit.extensions import (
    bcrypt,
    list_cache,
    cache,
    cors,
    db,
    migrate,
    elasticsearch,
    event_publisher
)
from reddit.events import EventPublisher, Event, EventConsumer
from reddit.jwt import jwt

import os


def configure(app):
    env_type = os.getenv("FLASK_ENV", "development")

    app.config.from_object(f"config.{env_type.title()}")


def register_extensions(app):
    bcrypt.init_app(app)
    list_cache.init_app(app)
    cache.init_app(app)
    cors.init_app(app)
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    event_publisher.init_app(app)

    # Allow for disabling during test.
    if app.config.get('ES_ENABLED') and app.config.get("ES_HOST"):
        # Custom search extension
        elasticsearch.init_app(app)
        # Add events for syncing relational data with other data stores
        #register_es_events(db)


def register_blueprints(app):
    app.register_blueprint(search.views.bp)
    app.register_blueprint(listing.views.bp)
    app.register_blueprint(subreddits.views.bp_sr)
    app.register_blueprint(subreddits.views.bp_ss)
    app.register_blueprint(threads.views.bp)
    app.register_blueprint(user.views.bp)
    app.register_blueprint(votes.views.bp)


def register_errorhandler(app):
    def errorhandler(error):
        response = jsonify({
            "message": error.message,
            "status_code": error.status_code
        })
        response.status_code = error.status_code
        return response

    app.errorhandler(InvalidUsage)(errorhandler)


def register_shellcontext(app):
    """Register shell context objects."""
    def shell_context():
        return {
            'db': db,
            'User': user.models.User,
            'Thread': threads.models.Thread,
            'Comment': threads.models.Comment,
            'Vote': votes.models.Vote
        }
    app.shell_context_processor(shell_context)


def register_commands(app):
    app.cli.add_command(commands.clean)
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.create_indexes)
    app.cli.add_command(commands.run_consumer)

def create_app():
    app = Flask(__name__)

    @app.route("/healthcheck")
    def healthcheck():
        return "OK"

    configure(app)
    register_blueprints(app)
    register_commands(app)
    register_errorhandler(app)
    register_extensions(app)
    register_shellcontext(app)

    return app
