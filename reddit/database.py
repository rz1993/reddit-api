from datetime import datetime
from flask import current_app
from flask_jwt_extended import current_user
from reddit.errors import InvalidUsage
from reddit.extensions import cache, db, event_publisher
from reddit.logging import logger


"""
Rewrite database layer so that interfaces are clean
Think about how to update number of comment and likes asynchronously or in batch (but also reliably)
    - One idea is we can be lazy and update the number on the database side on every read after one sec
    - This we act as a buffer behind the cache

TODO:
- Database objects broken up into "Entities" and "Actions"
    - Entities: e.g. user, post, comment, link
    - Actions: e.g. saved, liked, viewed, shared
- Entities should send events with following structure
    - Routing Key: [entity_type].[create/update/delete]
        - E.g. user.create, post.delete, comment.create
    - Body:
        - Data: Entity data
        - Context: timestamp
        - Metadata: anything relevant to that entity, but isn't stored in its body
- Actions:
    - TBD

- Read flow should be relatively simple:
    - Entities
        - If in cache then read from cache
        - If not in cache, then construct and store in cache before returning
        - Write through cache, to alleviate thundering herd
    - Lists
        - Lists should be kept in cache and updated
        - Same idea as read for entities
    - Actions

    - entity and list reads should be doable via decorator pattern
    - views where results are custom queries (no ids) require more than decorator pattern

- Write flow should be where complexity lies:
    - asynchronous write flows
    - entity creation writes should not be async (need to ensure that they occur before any subsequent updates)

"""

INVALID_HASH = {'_invalidated': True}

class CrudMixin(object):
    cache = cache

    id = db.Column(db.Integer, primary_key=True)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def _cache_prefix(cls):
        return cls.__name__

    @classmethod
    def make_cache_key(cls, id):
        return f'{cls._cache_prefix()}_{id}'

    @classmethod
    def make_cache_keys(cls, ids):
        prefix = cls._cache_prefix()
        return [f'{prefix}_{id}' for id in ids]

    def cache_key(self):
        return self.make_cache_key(self.id)

    @classmethod
    def get_from_cache(cls, id):
        cache = cls.cache
        key = cls.make_cache_key(id)
        logger.info(f"Getting cached key {key}")
        cached = cache.get(key)
        logger.info(f"Read cached value {cached}")
        if cached:
            if cached == INVALID_HASH:
                raise InvalidUsage.resource_not_found()
            cached = cls._serializer.load(cached)
        return cached

    @classmethod
    def get_from_db(cls, id, strict=False):
        obj = cls.query.get(id)
        if not obj and strict:
            raise InvalidUsage.resource_not_found()
        return obj

    @classmethod
    def get_or_404(cls, id):
        cached = cls.get_from_cache(id)
        if cached:
            return cached

        obj = cls.get_from_db(id, strict=True)

        status = obj.write_to_cache()
        return obj.serialize()

    def serialize(self):
        return self._serializer.dump(self)

    def write_to_cache(self):
        key = self.cache_key()
        logger.info(f"Writing to cache key {key}.")
        return self.cache.set(key, self.serialize())

    def invalidate_cache(self):
        key = self.cache_key()
        # TODO: hset key:invalidated to True with a TTL (so deleted objects dont search database)
        return self.cache.set(key, INVALID_HASH)

    def save(self, commit=True):
        if self.updatedAt:
            self.updatedAt = datetime.utcnow()
        db.session.add(self)
        commit and db.session.commit()

    def update(self, **kwargs):
        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)
            self.updatedAt = datetime.utcnow()

    def delete(self, commit=True, cache=True):
        db.session.delete(self)
        commit and db.session.commit()
        #if cache:
        #    self.invalidate_cache()

    def emit_create_event(self):
        event_publisher.publish_entity_event(
            entity_type=self.__tablename__,
            op_type='create',
            data=self.serialize(),
            timestamp=self.createdAt
        )

    def emit_delete_event(self, timestamp):
        event_publisher.publish_entity_event(
            entity_type=self.__tablename__,
            op_type='delete',
            data=self.serialize(),
            timestamp=timestamp
        )

    def emit_update_event(self, timestamp=None):
        event_publisher.publish_entity_event(
            entity_type=self.__tablename__,
            op_type='update',
            data=self.serialize(),
            timestamp=timestamp or self.updatedAt
        )


class VotableMixin(object):
    """
    TODO:
        - use vote table to create and add vote (somehow avoid circular imports)
        - optionally implement has_voted property given a current user
        - Simply voting API, should just allow POST, UPDATE, DELETE
    """
    score = db.Column(db.Integer, default=0)

    def add_vote(self, vote):
        direction = 1 if vote.direction else -1
        self.score += direction

    def update_vote(self, old_vote):
        update_score = -2 if old_vote.direction else 2
        self.score += update_score

    def delete_vote(self, vote):
        update_score = -1 if vote.direction else 1
        self.score += update_score

    @property
    def has_voted(self):
        return current_user

# Enable events to differentiate new, dirty and deleted models

def before_commit(session):
    session._changes = {
        'add': list(session.new),
        'update': list(session.dirty),
        'delete': list(session.deleted)
    }

db.event.listen(db.session, 'before_commit', before_commit)
