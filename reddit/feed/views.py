from flask import Blueprint, current_app, jsonify, request, url_for
from flask_jwt_extended import current_user, jwt_required
from reddit.subreddits.models import Subreddit, subscriptions
from reddit.threads.models import Thread
from reddit.threads.serializers import threads_schema
from reddit.user.models import User


bp = Blueprint('feed', __name__, url_prefix="/api/v1/feed")


def create_feed(user_id, page=1):
    """
    Inefficient feed creation at read time. Do a join on user subscribed subreddits
    and latest threads.
    """
    page_size = current_app.config["ITEMS_PER_PAGE"]
    feed = Thread.query.join(
        subscriptions,
        Thread.subreddit_id == subscriptions.c.subreddit_id
    )\
    .add_columns(Thread.id, Thread.title, Thread.description, Thread.author_id, Thread.createdAt)\
    .filter(subscriptions.c.subscriber_id == user_id)\
    .order_by(Thread.createdAt.desc())\
    .paginate(page=page, per_page=page_size, error_out=False)

    return feed


@bp.route('', methods=['GET'])
@jwt_required
def get_feed():
    page = request.args.get('page', 1)

    feed_page = create_feed(current_user.id, page=page)
    feed_data = threads_schema.dumps(feed_page.items)
    payload = {'feed': feed_data}
    meta = {}
    if feed_page.has_next:
        meta['next'] = url_for('get_feed', page=feed_page.next_num)
    if feed_page.has_prev:
        meta['prev'] = url_for('get_feed', page=feed_page.prev_num)

    return jsonify(
        data={'feed': feed_data},
        meta=meta
    )
