from datetime import datetime
from flask import current_app
from flask_jwt_extended import current_user
from reddit.errors import InvalidUsage
from reddit.extensions import db


class CrudMixin(object):
    id = db.Column(db.Integer, primary_key=True)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def get_or_404(cls, field_val, field_name=None, pk=True):
        if pk:
            obj = cls.query.get(field_val)
        else:
            obj = cls.query.filter_by(**{field_name: field_val})
        if not obj:
            raise InvalidUsage.resource_not_found()
        return obj

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()

    def update(self, **kwargs):
        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)
            self.updatedAt = datetime.utcnow()

    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            db.session.commit()


class VotableMixin(object):
    """
    TODO:
        - use vote table to create and add vote (somehow avoid circular imports)
        - optionally implement has_voted property given a current user
        - Simply voting API, should just allow POST, UPDATE, DELETE
    """
    score = db.Column(db.Integer, default=0)

    def add_vote(self, vote):
        direction = 1 if vote.direction else -1
        self.score += direction

    def update_vote(self, old_vote):
        update_score = -2 if old_vote.direction else 2
        self.score += update_score

    def delete_vote(self, vote):
        update_score = -1 if vote.direction else 1
        self.score += update_score

    @property
    def has_voted(self):
        return current_user

# Enable events to differentiate new, dirty and deleted models

def before_commit(session):
    session._changes = {
        'add': list(session.new),
        'update': list(session.dirty),
        'delete': list(session.deleted)
    }

db.event.listen(db.session, 'before_commit', before_commit)
