from reddit.database import CrudMixin, VotableMixin
from reddit.extensions import db
from datetime import datetime


class Comment(db.Model, CrudMixin, VotableMixin):
    __tablename__ = "comment"

    __searchable__ = ['body', 'author_id']

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = db.relationship("User", backref="comments")
    thread_id = db.Column(db.Integer, db.ForeignKey("thread.id"))
    thread = db.relationship("Thread", backref=db.backref("comments", lazy="dynamic"))


class Thread(db.Model, CrudMixin, VotableMixin):
    __tablename__ = "thread"

    __searchable__ = ['title', 'description', 'body', 'author_id', 'subreddit_id']

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String, nullable=False, unique=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text)
    #content_type = db.Column(db.Enum)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = db.relationship("User", backref="threads")
    num_comments = db.Column(db.Integer, default=0)

    subreddit_id = db.Column(db.Integer, db.ForeignKey("subreddits.id"))
    subreddit = db.relationship("Subreddit", backref=db.backref('threads', lazy='dynamic'))

    def __init__(self, **kwargs):
        if "title" not in kwargs:
            raise ValueError("Thread must be given a title.")
        slug = "-".join([w.lower() for w in kwargs["title"].split()])
        kwargs["slug"] = slug
        super(Thread, self).__init__(**kwargs)

    def add_comment(self, body, author, commit=True, **kwargs):
        comment = Comment(body=body, author=author,thread=self, **kwargs)
        try:
            comment.save(commit=False)
            self.num_comments += 1
            self.save(commit=commit)
        except Exception as ex:
            db.session.rollback()
            raise ex
        return comment

    def delete_comment(self, comment_id):
        comment = Comment.get_or_404(comment_id)
        try:
            if comment.thread_id != self.id:
                raise ValueError('Comment does not exist.')
            comment.delete(commit=False)
            self.num_comments -= 1
            self.save()
        except Exception as ex:
            db.session.rollback()
            raise ex
