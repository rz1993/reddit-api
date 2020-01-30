from flask import Blueprint, jsonify
from flask_apispec import marshal_with, use_kwargs
from flask_jwt_extended import current_user, jwt_required
from marshmallow import fields
from reddit.database import db
from reddit.errors import InvalidUsage
from reddit.threads.models import Thread
from reddit.votes.models import Vote
from reddit.votes.serializers import user_votes_schema, thread_votes_schema, vote_schema
from sqlalchemy import exc


bp = Blueprint("votes", __name__, url_prefix="/api/v1/vote")

@bp.route("", methods=["GET"])
@jwt_required
@use_kwargs({"thread": fields.Int(), "user": fields.Int()})
def get_votes(thread=None, user=None):
    if (thread is None and user is None) \
            or (thread is not None and user is not None):
        raise InvalidUsage.validation_error()

    res = Vote.query
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
@use_kwargs({"thread": fields.Int(required=True), "direction": fields.Int(required=True)})
def create_vote(thread=None, direction=None):
    if not direction or direction not in [-1, 1]:
        raise InvalidUsage.validation_error()

    thread = Thread.get_or_404(thread)

    try:
        vote = Vote(
            voter_id=current_user.id,
            voted_thread_id=thread.id,
            direction=direction
        )
        vote.save(commit=False)
        thread.add_vote(vote)
        thread.save(commit=True)
    except exc.IntegrityError as ex:
        db.session.rollback()
        raise InvalidUsage.duplicate()
    vote_data = vote_schema.dump(vote)
    return dict(
        message='Vote created',
        status=201
    ), 201


@bp.route("", methods=["PUT"])
@jwt_required
@use_kwargs({"thread": fields.Int(required=True), "direction": fields.Int(required=True)})
def update_vote(thread=None, direction=None):
    vote = Vote.get(current_user.id, thread)
    thread = Thread.get_or_404(thread)
    if not vote:
        raise InvalidUsage.resource_not_found()

    try:
        thread.update_vote(vote)
        vote.update(direction, commit=False)
        thread.save()
    except Exception as ex:
        db.session.rollback()
        raise InvalidUsage.duplicate()
    return dict(
        message='Vote updated.',
        status=204
    ), 204


@bp.route("", methods=["DELETE"])
@jwt_required
@use_kwargs({"thread": fields.Int(required=True)})
def delete_vote(thread=None):
    vote = Vote.get(current_user.id, thread)
    thread = Thread.get_or_404(thread)
    if not vote:
        raise InvalidUsage.resource_not_found()

    try:
        thread.delete_vote(vote)
        vote.delete(commit=False)
        thread.save()
    except Exception as ex:
        db.session.rollback()
        raise InvalidUsage.duplicate()

    return dict(
        message='Vote deleted',
        status=204
    ), 204

@bp.route("/count", methods=["GET"])
@use_kwargs({"thread": fields.Int(required=True)})
def get_vote_count(thread):
    counts = Vote.count_votes(thread)
    counts_by_direction = dict(counts)
    counts_by_direction['1'] = counts_by_direction.pop(True, 0)
    counts_by_direction['-1'] = counts_by_direction.pop(False, 0)
    
    return counts_by_direction
