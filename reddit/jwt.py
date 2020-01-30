from reddit.user.models import User
from flask_jwt_extended import JWTManager


def jwt_identity(payload):
    id = payload['id']
    return User.query.get(id)

def identity_loader(user):
    return {
        'id': user.id,
        'username': user.username
    }

jwt = JWTManager()
jwt.user_loader_callback_loader(jwt_identity)
jwt.user_identity_loader(identity_loader)
