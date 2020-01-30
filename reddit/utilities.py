from flask import jsonify
from functools import wraps
from reddit.errors import InvalidUsage


"""
Decorators
"""

def with_resource(model, field, primary_key=False):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if primary_key:
                object = model.query.get(kwargs.get(field))
            else:
                kwargs = {field: kwargs.get(field)}
                object = model.query.filter_by(**kwargs).first()

            if not object:
                raise InvalidUsage.resource_not_found()

            result = f(object, *args, **kwargs)

            return result
        return decorated
    return decorator

def marshal_with(schema, key='data', code=200, message=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            result = f(*args, **kwargs)
            response_dict = {
                key: schema.dump(result),
                'status': code
            }
            if message:
                response_dict['message'] = message
            return jsonify(response_dict), code
        return decorated
    return decorator
