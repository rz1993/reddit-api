from reddit.database import CrudMixin, db
from reddit.errors import InvalidUsage
from datetime import datetime


class Upvote(db.Model):
    __tablename__ = "upvotes"

    voter_id = db.Column(db.Integer, primary_key=True)
    voted_thread_id = db.Column(db.Integer, primary_key=True)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)

    def delete(self, commit=True):
        db.session.delete(self)
        return commit and db.session.commit()

    def save(self, commit=True):
        db.session.add(self)
        return commit and db.session.commit()

    @classmethod
    def get(cls, voter, voted):
        vote = cls.query.filter_by(voter_id=voter, voted_thread_id=voted).first()
        return vote

    @classmethod
    def count_upvotes(cls, thread_id):
        return cls.query.filter_by(voted_thread_id=thread_id).count()
