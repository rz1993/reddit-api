from datetime import datetime
from sqlalchemy import exc
from reddit.database import db, CrudMixin


subscriptions = db.Table(
    'subscriptions',
    db.Column('subscriber_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('subreddit_id', db.Integer, db.ForeignKey('subreddits.id'), primary_key=True),
    db.Column('createdAt', db.DateTime, default=datetime.utcnow)
)

class Subreddit(db.Model, CrudMixin):
    __tablename__ = 'subreddits'

    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    subscriber_count = db.Column(db.Integer, nullable=False, default=0)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref=db.backref('created_subreddits', lazy='dynamic'))
    subscribers = db.relationship('User',
        secondary='subscriptions',
        backref=db.backref(
            'subscribed_subreddits',
            lazy='dynamic'
        ),
        lazy='subquery'
    )

    def subscribe(self, user):
        try:
            self.subscribers.append(user)
            self.subscriber_count += 1
            self.save()
        except Exception as ex:
            db.session.rollback()
            raise ex

    def unsubscribe(self, user):
        try:
            self.subscribers.remove(user)
            self.subscriber_count -= 1
            self.save()
        except Exception as ex:
            db.session.rollback()
            raise ex
