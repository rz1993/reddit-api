from flask import Blueprint, jsonify
from flask_apispec import marshal_with, use_kwargs
from flask_jwt_extended import current_user, jwt_required
from marshmallow import fields
from reddit.database import db
from reddit.errors import InvalidUsage
from reddit.votes.models import Upvote
from reddit.votes.serializers import user_votes_schema, thread_votes_schema, vote_schema
from sqlalchemy import exc


bp = Blueprint("upvotes", __name__, url_prefix="/api/v1/upvote")

@bp.route("", methods=["GET"])
@jwt_required
@use_kwargs({"thread": fields.Int(), "user": fields.Int()})
def get_upvotes(thread=None, user=None):
    if (thread is None and user is None) \
            or (thread is not None and user is not None):
        raise InvalidUsage.validation_error()

    res = Upvote.query
    schema = None
    if thread:
        res = res.filter_by(voted_thread_id=thread).all()
        schema = thread_votes_schema
    elif user:
        res = res.filter_by(voter_id=user).all()
        schema = user_votes_schema
    return jsonify(
        data=schema.dump(res)
    )

@bp.route("", methods=["POST"])
@jwt_required
@use_kwargs({"thread": fields.Int(required=True)})
def create_vote(thread=None):
    try:
        vote = Upvote(voter_id=current_user.id, voted_thread_id=thread)
        vote.save()
    except exc.IntegrityError as ex:
        db.session.rollback()
        raise InvalidUsage.duplicate()
    vote_data = vote_schema.dump(vote)
    return jsonify(
        #data=vote_data,
        status=201,
        message="Upvote created."
    ), 201

@bp.route("", methods=["DELETE"])
@jwt_required
@use_kwargs({"thread": fields.Int(required=True)})
def delete_vote(thread=None):
    if thread is None:
        raise InvalidUsage.validation_error()

    vote = Upvote.get(current_user.id, thread)
    if not vote:
        raise InvalidUsage.resource_not_found()
    vote.delete()
    return jsonify(
        status=204,
        message="Upvote deleted."
    ), 204

@bp.route("/count", methods=["GET"])
@use_kwargs({"thread": fields.Int(required=True)})
def get_upvote_count(thread):
    count = Upvote.count_upvotes(thread)
    return jsonify(
        data={'count': count},
        status=200,
    ), 200
