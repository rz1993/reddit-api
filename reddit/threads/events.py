from blinker import signal
from reddit.extensions import cache, event_processor
from reddit.logging import logger
from reddit.threads.serializers import thread_schema, comment_schema
from reddit.threads.models import Comment, Thread


thread_create = signal('thread_create')
thread_update = signal('thread_update')
thread_delete = signal('thread_delete')

comment_create = signal('comment_create')
comment_update = signal('comment_update')
comment_delete = signal('comment_delete')


event_processor.register_crud_events(
    Thread,
    create=thread_create,
    update=thread_update,
    delete=thread_delete
)

event_processor.register_crud_events(
    Comment,
    create=comment_create,
    update=comment_update,
    delete=comment_delete
)

@thread_create.connect
def on_thread_create(thread):
    key = f'thread_{thread.id}'
    data = thread_schema.dumps(thread)
    logger.info(f'Caching thread {thread.id}')
    try:
        cache.set(key, data)
        logger.info('Finished caching thread.')
    except Exception as ex:
        logger.warning('Error occurred when caching.')

@comment_create.connect
def on_comment_create(comment):
    key = f'comment_{comment.id}'
    data = comment_schema.dumps(comment)
    logger.info(f'Caching comment: {comment.id}')
    try:
        cache.set(key, data)
        logger.info('Finished caching thread.')
    except Exception as ex:
        logger.warning('Error occurred when caching.')
