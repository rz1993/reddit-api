from marshmallow import Schema, fields, pre_dump, post_dump
from reddit.user.serializers import UserSchema


class SubredditSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    createdAt = fields.Str(dump_only=True)
    subscriber_count = fields.Int()
    creator = fields.Nested(UserSchema(only=('id', 'username')))


class SubredditsSchema(SubredditSchema):
    @post_dump(pass_many=True)
    def make_subreddits(self, data, many, **kwargs):
        return {
            'subreddits': data
        }


subreddit_schema = SubredditSchema()
subreddits_schema = SubredditsSchema(many=True)
