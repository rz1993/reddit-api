from flask import Blueprint, jsonify, request
from flask_apispec import marshal_with, use_kwargs
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError
from reddit.errors import InvalidUsage
from reddit.user.models import User
from reddit.user.serializers import user_schema
import reddit


bp = Blueprint("auth", __name__, url_prefix=f"/api/{reddit.__version__}/auth")

@bp.route("login", methods=["POST"])
def login():
    payload = request.get_json()
    if not payload:
        raise InvalidUsage.unknown_error()

    try:
        username = payload["username"]
        password = payload["password"]
    except KeyError as ex:
        raise InvalidUsage.unknown_error()

    user = User.query.filter_by(username=username).first()
    if not user or not user.verify(password):
        raise InvalidUsage.auth_failure()

    access_token = create_access_token(user)

    return jsonify(
        status=200,
        message='Success',
        data={'access_token': access_token}
    ), 200


@bp.route('register', methods=["POST"])
def register():
    payload = request.get_json()
    if not payload:
        raise InvalidUsage.validation_error()

    try:
        # Prevent user schema from breaking with no password field
        password = payload["password"]
        del payload["password"]

        data = user_schema.load(payload)
        data["password"] = password
    except ValidationError as ex:
        raise InvalidUsage.validation_error()
    except KeyError as ex:
        raise InvalidUsage.validation_error()
    except AssertionError as ex:
        raise InvalidUsage.unknown_error()

    user = User(**data)
    user.save()
    user_data = user_schema.dump(user)
    return jsonify(
        data={'user': user_data},
        message="Registration successful.",
        status=201
    ), 201
