from flask import Blueprint, current_app, jsonify, request, url_for
from flask_jwt_extended import current_user, jwt_optional, get_jwt_identity
from reddit.subreddits.models import Subreddit, subscriptions
from reddit.threads.models import Thread
from reddit.threads.serializers import threads_schema
from reddit.user.models import User
from reddit.utilities import with_time_logger


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
    .filter(subscriptions.c.subscriber_id == user_id)\
    .order_by(Thread.createdAt.desc())\
    .paginate(page=page, per_page=page_size, error_out=False)

    return feed


def create_generic_feed(page=1):
    page_size = current_app.config["ITEMS_PER_PAGE"]
    feed = Thread.query.order_by(Thread.createdAt.desc()).\
        paginate(page=page, per_page=page_size, error_out=False)
    return feed


@bp.route('', methods=['GET'])
@jwt_optional
@with_time_logger
def get_feed():
    page = request.args.get('page', 1)
    current_user = get_jwt_identity()

    if current_user:
        feed_page = create_feed(current_user['id'], page=page)
    if not current_user or len(feed_page.items) == 0:
        feed_page = create_generic_feed(page=page)

    feed_data = threads_schema.dump(feed_page.items)
    meta = {}
    if feed_page.has_next:
        meta['next'] = url_for('feed.get_feed', page=feed_page.next_num)
    if feed_page.has_prev:
        meta['prev'] = url_for('feed.get_feed', page=feed_page.prev_num)
    feed_data['meta'] = meta

    return jsonify(
        data=feed_data
    )
