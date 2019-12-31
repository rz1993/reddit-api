from marshmallow import Schema, fields, post_load, pre_load, post_dump
from reddit.user.models import User


class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    bio = fields.Str()
    createdAt = fields.DateTime(dump_only=True)
    updatedAt = fields.DateTime(dump_only=True)

    #@post_load
    #def make_user(self, data, **kwargs):
    #    return User(**data)

class UsersSchema(Schema):
    @post_dump(pass_many=True)
    def make_users(self, data, many, **kwargs):
        return {'users': data, 'userCount': len(data)}


user_schema = UserSchema()
users_schema = UsersSchema(many=True)
