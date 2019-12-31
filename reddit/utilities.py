from reddit.errors import InvalidUsage

"""
Decorators
"""

def with_resource(model, field, primary_key=False):
    def decorator(f):
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
