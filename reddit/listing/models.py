import json
from flask_jwt_extended import current_user
from itertools import chain
from reddit.cache import KEY_INVALID
from reddit.extensions import cache, db, list_cache
from reddit.logging import logger
from reddit.subreddits.models import Subreddit, subscriptions
from reddit.threads.models import Thread
from sqlalchemy import select

'''
Listing types:
- subreddit listing
- home feed listing
- search results listing (optional)

Listing retrieval API:
- subreddit listing
    - GET: subreddit, user_id, sort_type
- feed listing
    - GET: user_id
- search results
    - GET: query

High Level Implementation
- listings for a subreddit should be write through cached since they need to be fetched quickly
- listings for a user are frequently accessed, but doing write through cache for all members would be expensive
    - instead construct from listings of subreddit at read time
'''

class Listing:
    def __init__(self, items):
        self.items = items

    @classmethod
    def get(cls):
        raise NotImplementedError('Not implemented.')

    @classmethod
    def _get_from_cache(cls):
        raise NotImplementedError('Not implemented.')

    @classmethod
    def _get_from_db(cls):
        raise NotImplementedError('Not implemented.')

    def sort(self, sort_type=None):
        pass

    def serialize(self):
        pass


class SubredditListing(Listing):
    @classmethod
    def get(cls, subreddit_id):
        try:
            listing_objects = cls._get_from_cache(subreddit_id)
        except Exception as ex:
            logger.info(f"Encountered exception reading from cache: {ex}")
            logger.info(f"Fetching from database.")
            listing_objects = cls._get_from_db(subreddit_id)
        return cls(listing_objects)

    @classmethod
    def _get_from_cache(cls, subreddit_id):
        cache_key = Subreddit.make_cache_key(subreddit_id)
        logger.info(f"Getting subreddit listing from cache at key {cache_key}.")
        ids = list_cache.get(cache_key, start=0)
        ids_cache = Thread.make_cache_keys(map(str, ids))
        logger.info(f"Getting thread listing from cache with keys {ids[:5]}...")
        items = cache.get_many(ids_cache)

        # For the items not found in cache, fetch from database
        items_found = []
        items_not_found_ids = []
        for i in range(len(ids)):
            if items[i]:
                items_found.append(items[i])
            else:
                items_not_found_ids.append(ids[i])

        logger.info(f"Did not find {len(ids_not_found)} in cache.")
        if items_not_found_ids:
            logger.info("Fetching missing items from database.")
            items_found_in_db = self._get_from_db_w_ids(items_not_found_ids)
            logger.info(f"Found {len(items_found_in_db)}/{len(ids_not_found)} missing cache items in database.")
            items_found.extend(items_found_in_db)

        return items_found

    @classmethod
    def _get_from_db(cls, subreddit_id):
        items = Thread.query.filter_by(subreddit_id=subreddit_id)\
                              .order_by(Thread.createdAt.desc())\
                              .all()
                              #.paginate(page=page, per_page=per_page, error=False)
        items = [t.serialize() for t in items]
        return items

    @classmethod
    def _get_from_db_w_ids(cls, ids):
        items = Thread.query.filter(Thread.id.in_(ids)).all()
        items = [t.serialize() for t in items]
        return items


class UserFeedListing(Listing):
    @classmethod
    def get(cls, user_id):
        try:
            items = cls._get_from_cache(user_id)
        except Exception as ex:
            logger.info(f"Encountered exception reading from cache: {ex}")
            logger.info(f"Fetching from database.")
            items = cls._get_from_db(user_id)
        return cls(items)

    @classmethod
    def _get_from_cache(cls, user_id):
        # TODO: retrieve back ups from database
        query = select([subscriptions.c.subreddit_id])\
                .where(subscriptions.c.subscriber_id == user_id)
        sr_ids = db.engine.execute(query)
        sr_ids = Subreddit.make_cache_keys(map(lambda pair: pair[0], sr_ids))
        logger.info(f'Subreddit followed: {sr_ids}')
        sr_listing_ids = list_cache.get_many(sr_ids)
        sr_listing_ids = Thread.make_cache_keys(chain(*sr_listing_ids))
        logger.info(f"Fetched cached listing ids {sr_listing_ids[:5]}...")
        items = cache.get_many(sr_listing_ids)
        logger.info(f"Fetched {len(items)} cached items.")
        return items

    @classmethod
    def _get_from_db(cls, user_id):
        items = Thread.query.join(
                subscriptions,
                Thread.subreddit_id == subscriptions.c.subreddit_id
            )\
            .filter(subscriptions.c.subscriber_id == user_id)\
            .order_by(Thread.createdAt.desc())\
            .all()
        items = [t.serialize() for t in items]
        return items
