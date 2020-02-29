import json
import os
import pika
from datetime import datetime
from queue import Queue
from reddit.logging import logger

"""
EventQueue
- topics: [resource].[action]
    - RESOURCE=VOTE: vote.create, vote.update, vote.delete
    - RESOURCE=POST: post.create, post.update, post.delete
    - RESOURCE=COMMENT: comment.create, comment.update, comment.create

Make testing new consumers and jobs easier
"""

class RabbitMqConnectionPool:
    """
    Dummy Pool
    """
    def __init__(self, app=None):
        self.queue = Queue()
        self.connection_params = None
        self._connection = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.connection_params = pika.ConnectionParameters(
            host=app.config['RABBITMQ_HOST'],
            port=app.config['RABBITMQ_PORT'],
            heartbeat=app.config['RABBITMQ_HEARTBEAT'],
            blocked_connection_timeout=app.config['RABBITMQ_TIMEOUT']
        )

    def connection(self):
        if not self._connection or not self._connection.is_open:
            self._connection = pika.BlockingConnection(self.connection_params)
        return self._connection

    def channel(self):
        return self.connection().channel()


class EventPublisher:
    """
    TODO:
        - channel.declare_exchange(exchange_name='reddit', exchange_type='topic')
    """
    def __init__(self, app=None):
        self.exchange = None
        self.pool = None
        if app:
            self.init_app(app)

    @property
    def channel(self):
        return self.pool.channel()

    def init_app(self, app):
        logger.info(f"<EventPublisher> Connecting to RabbitMQ @ host:{app.config['RABBITMQ_HOST']} and port:{app.config['RABBITMQ_PORT']}")
        self.exchange = app.config['RABBITMQ_EXCHANGE']
        self.pool = RabbitMqConnectionPool(app)
        self.channel.exchange_declare(
            exchange=self.exchange,
            exchange_type='topic'
        )

    def send_event(self, event):
        routing_key = event.routing_key
        event_body = event.dump()
        logger.info(f"Sending event {routing_key} to exchange {self.exchange}")
        try:
            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=routing_key,
                body=event_body
            )
        except pika.exceptions.AMQPConnectionError as ex:
            logger.info(f"Could not connect to RabbitMQ when sending event {routing_key}.")
            # Fail silently for now

    def publish_entity_event(self, entity_type, op_type, data, timestamp, metadata=None):
        routing_key = f'{entity_type}.{op_type}'
        event = Event(
            routing_key,
            body=data,
            timestamp=timestamp
        )
        self.send_event(event)


class Event:
    def __init__(self, routing_key, body, timestamp=None):
        self.routing_key = routing_key
        self.body = body
        self.timestamp = timestamp or datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    def dump(self):
        return json.dumps({
            'body': self.body,
            'timestamp': str(self.timestamp), #TODO: do timestamp formatting and parsing
        })


class EventConsumer:
    def __init__(self, app=None):
        self.app = app
        self.pool = None
        if app:
            self.init_app(app)

    @property
    def channel(self):
        return self.pool.channel()

    @property
    def queue_name(self):
        if not self._queue_name:
            raise NotImplementedError('Consumer needs a queue name')
        return self._queue_name

    @property
    def routing_key(self):
        if not self._routing_key:
            raise NotImplementedError('Consumer needs a routing key')
        return self._routing_key

    def init_app(self, app):
        self.pool = RabbitMqConnectionPool(app)
        channel = self.channel

        exchange = app.config['RABBITMQ_EXCHANGE']
        channel.exchange_declare(
            exchange=exchange,
            exchange_type='topic'
        )

    def start(self):
        logger.info(f"<Queue:{self.queue_name}> Starting EventConsumer.")
        channel = self.channel
        exchange = self.app.config['RABBITMQ_EXCHANGE']
        queue_name = self.queue_name
        logger.info(f"<Queue:{self.queue_name}> Declaring queue.")
        result = channel.queue_declare(
            queue_name, durable=True
        )
        channel.queue_bind(
            exchange=exchange,
            queue=queue_name,
            routing_key=self.routing_key
        )
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=self.handle_event,
        )
        logger.info(f"<Queue:{self.queue_name}> Consuming.")
        channel.start_consuming()

    def handle_event(self, ch, method, properties, body):
        raise NotImplementedError('Implement an event handler.')
