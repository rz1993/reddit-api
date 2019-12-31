from flask import Blueprint, jsonify, request
from flask_apispec import marshal_with, use_kwargs
from flask_jwt_extended import current_user, jwt_required
from marshmallow import ValidationError
from reddit.errors import InvalidUsage
from reddit.subreddits.models import Subreddit
from reddit.threads.models import Comment, Thread
from reddit.threads.serializers import (
    comment_schema, comments_schema,
    thread_schema, threads_schema
)
import reddit


bp = Blueprint("thread", __name__, url_prefix=f"/api/{reddit.__version__}/threads")

"""
THREADS
"""

def parse_thread():
    data = request.json
    if not data or 'subreddit_name' not in data:
        raise InvalidUsage.validation_error()

    subreddit = data['subreddit_name']
    del data['subreddit_name']
    try:
        data = thread_schema.load(data)
    except ValidationError:
        raise InvalidUsage.validation_error()

    subreddit = Subreddit.query.filter_by(name=subreddit).first()
    if not subreddit:
        raise InvalidUsage.resource_not_found()
    data['subreddit'] = subreddit

    return data

def parse_comment():
    data = request.json
    if not data:
        raise InvalidUsage.validation_error()

    try:
        data = comment_schema.load(data)
    except ValidationError:
        raise InvalidUsage.validation_error()

    return data

@bp.route("/<int:id>", methods=["GET"])
@marshal_with(thread_schema)
def get_thread(id):
    thread = Thread.get_or_404(id)
    return thread

@bp.route("/<int:id>", methods=["PUT"])
@jwt_required
def update_thread(id):
    thread = Thread.get_or_404(id)
    if current_user.id != thread.author_id:
        raise InvalidUsage.unauthorized()

    data = parse_thread()
    thread.update(**data)
    thread.save()

    return jsonify(
        message='Update successful',
        status=204
    ), 204

@bp.route("/<int:id>", methods=["DELETE"])
@jwt_required
def delete_thread(id):
    thread = Thread.get_or_404(id)
    if current_user.id != thread.author_id:
        raise InvalidUsage.unauthorized()

    thread.delete()
    return jsonify(
        message='Delete successful',
        status=204
    ), 204

@bp.route("", methods=["POST"])
@marshal_with(thread_schema)
@jwt_required
def create_thread():
    data = parse_thread()
    data["author_id"] = current_user.id
    
    thread = Thread(**data)
    thread.save()
    return thread

"""
COMMENTS
"""

@bp.route("/<int:id>/comments", methods=["GET"])
def get_comments(id):
    thread = Thread.get_or_404(id)
    thread_data = comments_schema.dump(thread.comments)
    return jsonify(
        data=thread_data,
        status=200
    )

@bp.route("/<int:id>/comments", methods=["POST"])
@jwt_required
@marshal_with(comment_schema)
def create_comment(id):
    thread = Thread.get_or_404(id)
    data = parse_comment()
    data["thread_id"] = id
    data["author_id"] = current_user.id
    comment = Comment(**data)
    comment.save()
    return comment

@bp.route("/<int:id>/comments/<int:cid>", methods=["DELETE"])
@jwt_required
def delete_comment(id, cid):
    thread = Thread.get_or_404(id)
    comment = thread.comments.filter_by(id=cid).first()
    if not comment:
        raise InvalidUsage.resource_not_found()
    if comment.author_id != current_user.id:
        raise InvalidUsage.unauthorized()

    comment.delete()
    return jsonify(
        message="Delete successful",
        status=204
    ), 204

@bp.route("/<int:id>/comments/<int:cid>", methods=["PUT"])
@jwt_required
def update_comment(id, cid):
    thread = Thread.get_or_404(id)
    comment = thread.comments.filter_by(id=cid).first()
    if not comment:
        raise InvalidUsage.resource_not_found()
    if comment.author_id != current_user.id:
        raise InvalidUsage.unauthorized()

    data = parse_comment()
    comment.update(**data)
    comment.save()

    return jsonify(
        message="Success",
        status=204
    ), 204
