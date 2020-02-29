from reddit.database import CrudMixin, db
from reddit.errors import InvalidUsage
from sqlalchemy import func as sql_func
from datetime import datetime

"""
TODO: Make votes directional and allowed for Comments AND Threads
"""

def direction_to_bool(direction):
    if direction == -1:
        return False
    elif direction == 1:
        return True
    else:
        raise ValueError('Vote direction must be either `-1` or `1`.')

class Vote(db.Model):
    __tablename__ = "votes"

    voter_id = db.Column(db.Integer, primary_key=True)
    voted_thread_id = db.Column(db.Integer, primary_key=True)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    direction = db.Column(db.Boolean, nullable=False)

    def __init__(self, direction=None, **kwargs):
        super(Vote, self).__init__(
            direction=direction_to_bool(direction),
            **kwargs
        )

    def update(self, direction, commit=True):
        new_direction = direction_to_bool(direction)
        if new_direction == self.direction:
            raise ValueError('New vote direction must be different.')
        self.direction = new_direction
        self.save(commit=commit)

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
    def has_voted(cls, objects, user):
        object_ids = [o['id'] for o in objects]
        raise NotImplementedError()

    @classmethod
    def count_votes(cls, thread_id):
        """
        SELECT DIRECTION, COUNT(id)
        FROM votes
        GROUP BY DIRECTION
        """
        return cls.query\
            .with_entities(cls.direction, sql_func.count(cls.voter_id))\
            .group_by(cls.direction)\
            .filter_by(voted_thread_id=thread_id)\
            .all()
