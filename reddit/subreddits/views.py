from flask import Blueprint, jsonify, request
from flask_apispec import use_kwargs
from flask_jwt_extended import current_user, jwt_required
from marshmallow import fields, ValidationError
from reddit import __version__
from reddit.errors import InvalidUsage
from reddit.subreddits.serializers import subreddit_schema, subreddits_schema
from reddit.subreddits.models import Subreddit
from sqlalchemy import exc


bp_sr = Blueprint('subreddits', __name__, url_prefix=f'/api/{__version__}/subreddits')
bp_ss = Blueprint('subscriptions', __name__, url_prefix=f'/api/{__version__}/subscriptions')


@bp_sr.route('<string:name>', methods=['GET'])
def get_subreddit(name):
    subreddit = Subreddit.query.filter_by(name=name).first()
    if not subreddit:
        raise InvalidUsage.resource_not_found()

    data = subreddit_schema.dump(subreddit)
    return jsonify(
        data={'subreddit': data},
        status=200
    )


@bp_sr.route('', methods=['POST'])
@jwt_required
def create_subreddit():
    data = request.get_json()
    try:
        subreddit_data = subreddit_schema.load(data)
        subreddit = Subreddit(creator_id=current_user.id, **subreddit_data)
        subreddit.save()

        subreddit.subscribe(current_user)
    except ValidationError as ex:
        raise InvalidUsage.validation_error()
    except exc.IntegrityError as ex:
        raise InvalidUsage.duplicate()
    subreddit_data = subreddit_schema.dump(subreddit)
    return jsonify(
        data={'subreddit': subreddit_data},
        message='Subreddit created.',
        status=201
    ), 201


@bp_ss.route('', methods=['PUT'])
@use_kwargs({'subreddit': fields.Str(required=True)})
@jwt_required
def subscribe(subreddit):
    subreddit = Subreddit.query.filter_by(name=subreddit).first()
    if not subreddit:
        raise InvalidUsage.resource_not_found()

    try:
        subreddit.subscribe(current_user)
    except exc.IntegrityError:
        raise InvalidUsage.duplicate()
    return jsonify(message='Subscribed.', status=204)


@bp_ss.route('', methods=['DELETE'])
@use_kwargs({'subreddit': fields.Str(required=True)})
@jwt_required
def unsubscribe(subreddit):
    subreddit = Subreddit.query.filter_by(name=subreddit).first()
    if not subreddit:
        raise InvalidUsage.resource_not_found()

    try:
        subreddit.unsubscribe(current_user)
    except ValueError as ex:
        raise InvalidUsage.resource_not_found()
    except Exception as ex:
        raise InvalidUsage.unknown_error()

    return jsonify(message='Unsubscribed.', status=204)


@bp_ss.route('subscriptions', methods=['GET'])
@jwt_required
def get_subscriptions():
    subreddit = Subreddit.query.filter_by(name=name).first()
    if not subreddit:
        raise InvalidUsage.resource_not_found()

    data = subreddit_schema.dump(subreddit_schema)
    return jsonify(
        data=data,
        status=200
    )
