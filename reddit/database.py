from datetime import datetime
from flask import current_app
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

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs):
        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)
            self.updatedAt = datetime.utcnow()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
