"""Module for elasticsearch functionality."""

# TODO: Add subreddit specific search
# TODO: Add result boosting based on likes/etc

from flask import current_app


def add_to_index(index, model):
    """
    :param index:   Elasticsearch index to add model to
    :param model:   Instance of a SQLAlchemy Model representing a record
    """
    if current_app.elasticsearch is None:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, id=model.id, body=payload)


def delete_from_index(index, model):
    """
    :param index:   Elasticsearch index to add model to
    :param model:   Instance of a SQLAlchemy Model representing a record
    """
    if current_app.elasticsearch is None:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)


def search_index(index, query, page, per_page):
    """
    :param index:   Elasticsearch index to add model to
    :param query:   Text query to search elasticsearch index for.
    """
    if current_app.elasticsearch is None:
        return
    results = current_app.elasticsearch.search(
        index=index,
        body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
              'from': (page-1)*per_page, 'size': per_page}
    )
    ids = [int(hit['_id']) for hit in results['hits']['hits']]
    return ids, results['hits']['total']
