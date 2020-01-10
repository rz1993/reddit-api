from datetime import datetime
from flask import current_app
from reddit.errors import InvalidUsage
from reddit.extensions import db, elasticsearch


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


def before_commit(session):
    session._changes = {
        'add': list(session.new),
        'update': list(session.dirty),
        'delete': list(session.deleted)
    }


def after_commit(session):
    for obj in session._changes['add']:
        if elasticsearch.is_searchable(obj):
            elasticsearch.add_document(obj)

    for obj in session._changes['update']:
        if elasticsearch.is_searchable(obj):
            elasticsearch.update_document(obj)

    for obj in session._changes['delete']:
        if elasticsearch.is_searchable(obj):
            elasticsearch.delete_document(obj)

    session._changes = None


db.event.listen(db.session, 'before_commit', before_commit)
db.event.listen(db.session, 'after_commit', after_commit)
