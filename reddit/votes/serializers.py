from marshmallow import fields, post_dump, Schema
from reddit.user.serializers import UserSchema


class VoteSchema(Schema):
    voter_id = fields.Int()
    voted_thread_id = fields.Int()
    createdAt = fields.DateTime(dump_only=True)
    direction = fields.Int()


class UserVotesSchema(Schema):
    voted_thread_id = fields.Int()

    @post_dump(pass_many=True)
    def make_votes(self, data, many, **kwargs):
        return {"votes": data}


class ThreadVotesSchema(Schema):
    voter_id = fields.Int()

    @post_dump(pass_many=True)
    def make_votes(self, data, many, **kwargs):
        return {"votes": data}


vote_schema = VoteSchema()
user_votes_schema = UserVotesSchema(many=True)
thread_votes_schema = ThreadVotesSchema(many=True)
