from datetime import datetime
from flask import current_app
from reddit.errors import InvalidUsage
from reddit.extensions import db
from reddit.search import add_to_index, delete_from_index, search_index


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


class SearchableMixin(object):
    """
    Mixin to integrate Elasticsearch functionality with model data.
    Elasticsearch returns a list of model id's, but we want to provide the actual models
    the id's are associated with.
    In order to keep elasticsearch indices in-sync with database state, use
    SQLAlchemy events to trigger indexing and updates.
    """
    @classmethod
    def search(cls, index, query, page=1):
        page_size = current_app.config["ITEMS_PER_PAGE"]
        ids, num_results = search_index(index, query, page, page_size)
        models = cls.query.filter(cls.id.in_(ids)).all()
        return models, num_results

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'deleted': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        try:
            for obj in session._changes['add']:
                if isinstance(obj, SearchableMixin):
                    add_to_index(cls.__tablename__, obj)
            for obj in session._changes['deleted']:
                if isinstance(obj, SearchableMixin):
                    delete_from_index(cls.__tablename__, obj)
            session._changes = None
        except Exception as ex:
            """
            TODO: If fails, then queue this trigger somewhere and retry again.
            """
            raise ex


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)
