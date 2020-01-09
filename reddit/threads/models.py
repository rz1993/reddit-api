from reddit.database import CrudMixin, SearchableMixin
from reddit.extensions import db
from datetime import datetime


class Comment(db.Model, CrudMixin, SearchableMixin):
    __tablename__ = "comment"

    __searchable__ = ['body']

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = db.relationship("User", backref="comments")
    thread_id = db.Column(db.Integer, db.ForeignKey("thread.id"))
    thread = db.relationship("Thread", backref=db.backref("comments", lazy="dynamic"))


class Thread(db.Model, CrudMixin):
    __tablename__ = "thread"

    __searchable__ = ['title', 'description', 'body']

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String, nullable=False, unique=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text)
    #content_type = db.Column(db.Enum)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = db.relationship("User", backref="threads")

    subreddit_id = db.Column(db.Integer, db.ForeignKey("subreddits.id"))
    subreddit = db.relationship("Subreddit", backref=db.backref('threads', lazy='dynamic'))

    def __init__(self, **kwargs):
        if "title" not in kwargs:
            raise ValueError("Thread must be given a title.")
        slug = "-".join([w.lower() for w in kwargs["title"].split()])
        kwargs["slug"] = slug
        super(Thread, self).__init__(**kwargs)
