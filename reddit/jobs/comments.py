from flask import current_app
from reddit.logging import logger
from reddit.threads.models import Thread
from reddit.events import EventConsumer, Event
from reddit.extensions import cache
import json


class CommentConsumer(EventConsumer):
    _queue_name = 'comment_queue'
    _routing_key = 'comment.*'

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
        logger.info(f"Handling comment.create. {body}")
        try:
            body = json.loads(body)['body']
            thread_id = body['thread_id']

            thread_cache_key = Thread.make_cache_key(thread_id)
            cache.incr_field(thread_cache_key, 'num_comments', 1)
            # Acknowledgement
            ch.basic_ack(delivery_tag=method.delivery_tag)

            logger.info("Finished updating number of comments in cache.")
        except json.JSONDecodeError as ex:
            logger.warning("Error while decoding json:", str(ex))

    def handle_delete(self, ch, method, properties, body):
        logger.info(f"Handling comment.delete. {body}")
        try:
            body = json.loads(body)['body']
            thread_id = body['thread_id']

            thread_cache_key = Thread.make_cache_key(thread_id)
            cache.incr_field(thread_cache_key, 'num_comments', -1)
            # Acknowledgement
            ch.basic_ack(delivery_tag=method.delivery_tag)

            logger.info("Finished updating number of comments in cache.")
        except json.JSONDecodeError as ex:
            logger.warning("Error while decoding json:", str(ex))

    def handle_update(self, ch, method, properties, body):
        ch.basic_ack(delivery_tag=method.delivery_tag)
