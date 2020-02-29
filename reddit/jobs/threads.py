from flask import current_app
from reddit.logging import logger
from reddit.subreddits.models import Subreddit
from reddit.threads.models import Thread
from reddit.events import EventConsumer, Event
from reddit.extensions import list_cache, cache
import json


class ThreadConsumer(EventConsumer):
    _queue_name = 'thread_queue'
    _routing_key = 'thread.*'

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
        logger.info(f"Handling create. {body}")
        try:
            body = json.loads(body)['body']
            thread_id = body['id']
            sr_id = body['subreddit_id']

            sr_list_key = Subreddit.make_cache_key(sr_id)
            list_cache.lpush(sr_list_key, thread_id)
            # Acknowledgement
            ch.basic_ack(delivery_tag=method.delivery_tag)

            logger.info("Finished updating Post list cache.")
        except json.JSONDecodeError as ex:
            logger.warning("Error while decoding json:", str(ex))

    def handle_delete(self, ch, method, properties, body):
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def handle_update(self, ch, method, properties, body):
        ch.basic_ack(delivery_tag=method.delivery_tag)
