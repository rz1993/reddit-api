from flask import Flask, jsonify
from reddit import subreddits, threads, user, votes
from reddit import commands
from reddit.errors import InvalidUsage
from reddit.extensions import bcrypt, cors, db, migrate
from reddit.jwt import jwt


def configure(app):
    import os

    env_type = os.getenv("FLASK_ENV", "development")

    app.config.from_object(f"config.{env_type.title()}")


def register_extensions(app):
    bcrypt.init_app(app)
    cors.init_app(app)
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
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
            'Upvote': votes.models.Upvote
        }
    app.shell_context_processor(shell_context)


def register_commands(app):
    app.cli.add_command(commands.clean)
    app.cli.add_command(commands.test)


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

    return app
