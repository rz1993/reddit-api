from marshmallow import Schema, fields, pre_load, post_dump
from reddit.subreddits.serializers import SubredditSchema
from reddit.user.serializers import UserSchema


class CommentSchema(Schema):
    id = fields.Int()
    body = fields.Str()
    createdAt = fields.DateTime()
    updatedAt = fields.DateTime(dump_only=True)
    author = fields.Nested(UserSchema(only=("id", "username")))


class CommentsSchema(CommentSchema):
    @post_dump(pass_many=True)
    def make_comments(self, data, many, **kwargs):
        return {'comments': data, 'commentCount': len(data)}


class ThreadSchema(Schema):
    id = fields.Int()
    slug = fields.Str()
    createdAt = fields.DateTime()
    updatedAt = fields.DateTime()
    author = fields.Nested(UserSchema(only=("id", "username")), dump_only=True)
    subreddit = fields.Function(lambda obj: obj.subreddit.name, dump_only=True)
    body = fields.Str()
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    numComments = fields.Int(attribute='num_comments')
    score = fields.Int()

class ThreadsSchema(ThreadSchema):
    @post_dump(pass_many=True)
    def make_threads(self, data, many, **kwargs):
        return {'threads': data, 'threadCount': len(data)}


comment_schema = CommentSchema()
comments_schema = CommentsSchema(many=True)
thread_schema = ThreadSchema()
threads_schema = ThreadsSchema(many=True)
