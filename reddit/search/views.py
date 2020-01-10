from flask import Blueprint, jsonify, request
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch, Match
from reddit.errors import InvalidUsage


bp = Blueprint("search", __name__, url_prefix="/api/v1/search")


@bp.route('', methods=['GET'])
def search():
    try:
        query = request.args['q']
    except KeyError as ex:
        raise InvalidUsage.validation_error()
    
    search = Search(index='threads')
    search.query = MultiMatch(query=query, fields=['title', 'body', 'description'])
    response = search.execute()
    return jsonify(response.to_dict())
