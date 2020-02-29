import copy
import json
import redis
from reddit.logging import logger


KEY_INVALID = 'KEY_INVALID'

"""
Cache:
    - get, set, get_multi(prefix, stale), set_multi(prefix, ids)

Should be a mixin that defines a custom commit/save procedure which writes the object to cache
Mixin:
    - should define cache_key method so each instance can generate cache key
    - should have save procedure which also caches the object (actually want to do this to minimize network time, so find a way to batch requests)
    - GETs should check cache first
"""

def serialize(val):
    if hasattr(val, 'serialize'):
        return json.dumps(val.serialize())
    else:
        return json.dumps(val.encode('utf8'))

def deserialize(val):
    return json.loads(val)

def redis_decode(obj_bin):
    return {k.decode('ascii'): v.decode('ascii') for k, v in obj_bin.items()}


class AppCache:
    def __init__(self, name, app=None):
        #self.backend = redis.Redis(host='localhost', port='6379')
        self.name = name
        self.backend = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.backend = redis.Redis(
            host=app.config[f'{self.name.upper()}_CACHE_HOST'],
            port=app.config[f'{self.name.upper()}_CACHE_PORT']
        )

    def pipeline(self):
        return self.backend.pipeline()


class ObjectCache(AppCache):
    """
    Cache Interface:
        - get, set, delete, get_multi, set_multi
        -
        - TODO:
            - read-modify-delete with locks
    """
    def get(self, key):
        data = self.backend.hgetall(key)
        data = redis_decode(data) if data else None
        return data

    def get_many(self, keys, prefix=None):
        if prefix:
            keys = (f'{prefix}_{k}' for k in keys)

        pipe = self.backend.pipeline()
        pipe.multi()
        for k in keys:
            pipe.hgetall(k)

        objs = []
        for obj_dict in pipe.execute():
            if obj_dict:
                obj_dict = redis_decode(obj_dict)
            objs.append(obj_dict)

        return objs

    def set(self, key, val):
        try:
            logger.info(f"Caching {val}")
            return self.backend.hmset(key, val)
        except redis.exceptions.RedisError as ex:
            logger.info("Error while caching data", str(ex))

    def set_many(self, keys, vals):
        pipe = self.backend.pipeline()
        pipe.multi()
        try:
            for key, val in zip(keys, vals):
                pipe.hmset(key, val)
            pipe.execute()
        except redis.exceptions.RedisError as ex:
            logger.info("Error while caching data", str(ex))
        return True

    def incr_field(self, key, field, value=1):
        return self.backend.hincrby(key, field, value)

    def update_field(self, key, field, value):
        return self.backend.hset(key, field, value)

    def update_fields(self, key, field_mapping):
        return self.backend.hmset(key, field_mapping)

    def delete(self, key):
        return self.backend.delete(key)

    def delete_many(self, keys):
        return self.backend.mdelete(keys)

    def cached(self, cache_args, timeout=60, key_prefix=None, schema=None):
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                key = '-'.join(kwargs[key] for k in cache_args)
                if key_prefix:
                    key = f'{key_prefix}_{key}'

                val = self.get(key)
                if val and time.time() - float(val['_cached_timestamp']) <= timeout:
                    result = val
                    result.pop('_cached_timestamp')
                else:
                    result = f(*args, **kwargs)
                    result_cached = result.copy()
                    result_cached['_cached_timestamp'] = time.time()

                    self.set(key, result_cached)

                return result
            return decorated
        return decorator


class ListCache(AppCache):
    def __init__(self, *args, **kwargs):
        self.size_limit = None
        super().__init__(*args, **kwargs)

    def init_app(self, app):
        self.size_limit = app.config['LIST_CACHE_SIZE_LIMIT']
        super().init_app(app)

    def lpush(self, key, val):
        pipe = self.backend.pipeline()
        # Push and trim the list so it remains fixed size
        pipe.multi()
        pipe.lpush(key, val)
        pipe.ltrim(key, 0, self.size_limit)
        return pipe.execute()

    def _decode(self, vals):
        return list(map(lambda v: v.decode('ascii'), vals))

    def get(self, key, start=0, end=None):
        end = end or self.size_limit
        if start > end:
            raise ValueError('Redis range must be a valid index range.')
        raw_items = self.backend.lrange(key, start, end)
        return self._decode(raw_items)

    def get_many(self, keys, start=0, end=None):
        end = end or self.size_limit
        if start > end:
            raise ValueError('Redis range must be a valid index range.')
        pipe = self.backend.pipeline()
        pipe.multi()
        for k in keys:
            pipe.lrange(k, start, end)
        raw_items_many = pipe.execute()
        items_many = list(map(self._decode, raw_items_many))
        return items_many
