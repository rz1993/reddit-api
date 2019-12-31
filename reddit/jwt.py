from reddit.user.models import User
from flask_jwt_extended import JWTManager


def jwt_identity(payload):
    return User.query.get(payload)

def identity_loader(user):
    return user.id

jwt = JWTManager()
jwt.user_loader_callback_loader(jwt_identity)
jwt.user_identity_loader(identity_loader)
