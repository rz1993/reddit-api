"""Database events"""

from reddit.extensions import db, elasticsearch


def before_commit_sync_es(session):
    session._changes = {
        'add': list(session.new),
        'update': list(session.dirty),
        'delete': list(session.deleted)
    }


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
    'before_commit': [before_commit_sync_es],
    'after_commit': [after_commit_sync_es]
}
