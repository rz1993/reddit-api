from flask import current_app
from reddit.events import EventConsumer, Event
from reddit.logging import logger
from reddit.extensions import list_cache, cache
from reddit.subreddits.models import Subreddit
from reddit.threads.models import Thread
import json


class VoteConsumer(EventConsumer):
    _queue_name = 'vote_queue'
    _routing_key = 'vote.*'

    def handle_event(self, ch, method, properties, body):
        route_parts = method.routing_key.split('.')
        entity_type, op_type = route_parts[:2]
        if op_type == 'create':
            return self.handle_create(ch, method, properties, body)
        elif op_type == 'update':
            return self.handle_update(ch, method, properties, body)
        elif op_type == 'delete':
            return self.handle_delete(ch, method, properties, body)

    def handle_create(self, ch, method, props, body):
        logger.info("New vote created; atomically updating scores.")
        try:
            body = json.loads(body)['body']
            post_id = body['voted_thread_id']
            user_id = body['voter_id']
            direction = body['direction']
        except json.JSONDecodeError as ex:
            logger.info("Error while decoding json:", str(ex))

        thread_key = Thread.make_cache_key(post_id)
        return cache.incr_field(thread_key, 'score', value=direction)

    def handle_delete(self, ch, method, props, body):
        logger.info("Vote deleted; atomically updating scores.")
        try:
            body = json.loads(body)['body']
            post_id = body['voted_thread_id']
            user_id = body['voter_id']
            direction = body['direction']
        except json.JSONDecodeError as ex:
            logger.info("Error while decoding json:", str(ex))

        thread_key = Thread.make_cache_key(post_id)
        return cache.incr_field(thread_key, 'score', value=direction * -1)

    def handle_update(self, ch, method, props, body):
        logger.info("Vote updated; atomically updating scores.")
        try:
            body = json.loads(body)['body']
            post_id = body['voted_thread_id']
            user_id = body['voter_id']
            direction = body['direction']
        except json.JSONDecodeError as ex:
            logger.info("Error while decoding json:", str(ex))

        thread_key = Thread.make_cache_key(post_id)
        return cache.incr_field(thread_key, 'score', direction * -1 * 2)
