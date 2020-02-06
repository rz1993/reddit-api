"""Extension for syncing Elasticsearch indexes with SqlAlchemy models"""

from elasticsearch_dsl import Document
from elasticsearch_dsl.connections import connections
from reddit.extensions import db


# TODO: Figure out how to properly handle events
# NOTE: Current approach resulted in circular import

class ElasticsearchSql:
    __table_to_index__ = {}

    def __init__(self, app=None):
        self.initialized = False
        if app:
            self.init_app(app)

    def init_app(self, app):
        if not app.config.get('ES_HOST'):
            raise ValueError('A `ES_HOST` parameter must be specified to use Elasticsearch.')
        connections.create_connection(hosts=[app.config['ES_HOST']], timeout=20)
        self.initialized = True
        """
        conn = connections.get_connection()
        print("Connected to ES Cluster:")
        print("========================")
        print(conn.cluster.health())
        """

    def register_sql_model(self, model_cls, index_cls):
        if not issubclass(model_cls, db.Model):
            raise ValueError("`model_cls` must be a subclass of `FlaskSQLAlchemy.Model`")
        if not issubclass(index_cls, Document):
            raise ValueError("`index_cls` must be a subclass of elasticsearch_dsl.Document")

        if not getattr(model_cls, '__searchable__', None):
            raise ValueError(f"{model_cls.__name__} does not have any searchable fields.")

        if model_cls.__tablename__ in self.__table_to_index__:
            raise ValueError(f"{model_cls.__tablename__} is already registered under another"
                              "index")
        self.__table_to_index__[model_cls.__tablename__] = index_cls

    def create_all(self):
        if not self.initialized:
            raise Exception('Please create an app context.')
        for index_class in self.__table_to_index__.values():
            index_class.init()

    def _get_assoc_index(self, model_obj):
        try:
            EsIndexClass = self.__table_to_index__[model_obj.__tablename__]
        except KeyError as ex:
            raise ValueError(f"{model_obj.__class__.__name__} does not correspond"
                             "to a search index.")
        return EsIndexClass

    def is_searchable(self, model_obj):
        return model_obj.__tablename__ in table_to_index

    def map_to_document(self, model_obj):
        EsIndexClass = self._get_assoc_index(model_obj)
        data = {}
        for attr in model_obj.__searchable__:
            data[attr] = getattr(model_obj, attr)
        document = EsIndexClass(meta={'id': model_obj.id}, **data)
        return document

    def add_document(self, model_obj):
        document = self.map_to_document(model_obj)
        document.save()
        return document

    def update_document(self, model_obj):
        document = self.map_to_document(model_obj)
        document.update(retry_on_conflict=2)
        return document

    def delete_document(self, model_obj):
        document = self.map_to_document(model_obj)
        document.delete()
        return True


def after_commit_sync_es(session):
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


EVENT_REGISTRY = {
    'after_commit': [after_commit_sync_es]
}
