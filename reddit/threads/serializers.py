from marshmallow import Schema, fields, pre_load, post_dump
from reddit.subreddits.serializers import SubredditSchema
from reddit.user.serializers import UserSchema


class CommentSchema(Schema):
    id = fields.Int()
    body = fields.Str()
    createdAt = fields.DateTime()
    updatedAt = fields.DateTime()
    author = fields.Nested(UserSchema(only=("id", "username")))


class CommentsSchema(CommentSchema):
    @post_dump(pass_many=True)
    def make_comments(self, data, many, **kwargs):
        return {'comments': data, 'commentCount': len(data)}


def deserialize_sr(d):
    print(f"====DESERIALIZING SUBREDDIT====: {d}")


class ThreadSchema(Schema):
    id = fields.Int()
    slug = fields.Str()
    createdAt = fields.DateTime()
    updatedAt = fields.DateTime()
    #author = fields.Nested(UserSchema(only=("id", "username")), dump_only=True)
    author = fields.Function(serialize=lambda obj: obj.author.username, deserialize=lambda v: v)
    subreddit_id = fields.Int()
    subreddit = fields.Function(serialize=lambda obj: obj.subreddit.name, deserialize=lambda v: v)
    #body = fields.Str()
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
