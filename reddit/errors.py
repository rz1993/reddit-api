def template(data, code=500):
    return {'message': {'error': {'body': data}}, 'status_code': code}


DUPLICATE_RESOURCE = template('Resource already exists', code=442)
USER_NOT_FOUND = template('User not found', code=404)
RESOURCE_NOT_FOUND = template('Resource does not exist', code=404)
AUTH_FAILURE = template('Authentication failed', code=401)
UNAUTHORIZED = template('Unauthorized action', code=403)
VALIDATION_ERROR = template('Incorrect payload format', code=422)
UNKNOWN_ERROR = template('', code=500)

class InvalidUsage(Exception):
    status_code = 500

    def __init__(self, message, status_code=500, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    @classmethod
    def resource_not_found(cls):
        return cls(**RESOURCE_NOT_FOUND)

    @classmethod
    def user_not_found(cls):
        return cls(**USER_NOT_FOUND)

    @classmethod
    def duplicate(cls):
        return cls(**DUPLICATE_RESOURCE)

    @classmethod
    def unknown_error(cls):
        return cls(**UNKNOWN_ERROR)

    @classmethod
    def auth_failure(cls):
        return cls(**AUTH_FAILURE)

    @classmethod
    def unauthorized(cls):
        return cls(**UNAUTHORIZED)

    @classmethod
    def validation_error(cls):
        return cls(**VALIDATION_ERROR)
