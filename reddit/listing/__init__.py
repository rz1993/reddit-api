from . import views
"""
Requirements:
    - A set of APIs for returning a listing of threads for any subreddit, home feed
    - GET:
        - :param rank_type: ['hot', 'recent', 'top']
        - :param page:      default 1
        - :param page_size: 20

    - Allow for different sorting methods
        - Hot, Recent, (Optionally Controversial)
    - Updates should be reflected in the listing
    - Since feed is long, pagination should be consistent (despite frequent updates)

Implementation:
    - Home Feed
        - If user has no followed subreddits, then fall back to generic
        - Each subreddit has its own cache key, which stores list of newly created thread_id
            - Number of subreddits fewer than number of users
            - Relatively inexpensive to cache and retrieve thread data for most recent threads
            - Now do not need to propagate updates to each user after a new thread is created
            - Saves a lot of computation for large subs
        - Subscriptions for a user are also cached
        - Essentially in memory join of followed subreddits and newest threads for those subreddits
            - Scatter gather and hydrate
            - Merge, score and sort
            - Filter for any deleted
        - Assuming S subreddits, T new threads per sub, this would require:
            - 1 fetch followed subreddits
            - S requests to gather thread_ids for new subs
            - S requests (T gets each) to gather thread data
            - Last two can potentially be merged
        - Pros:
            - No massive updates
            - Only 1 replicated cached instance of any thread
        - Cons:
            - Fetching feeds costs 3 network requests and O(N) memory lookups
            - Sorting and ranking may be too expensive at query time

        - We can tweak the read path complexity by choosing degree of denormalization
            - precompute the score for an item and update it based on activity
            - precompute features necessary to compute the score (if relatively static compare to score itself)
            - precompute thread_ids for a user

        - Write Path
            - Need to figure out write cache strategy (cache on write or cache on read)
            - Need to figure out whether to store denormalized form
            - New Post written
                - After commit to database, post is added to Redis cache for subreddit
                    - Store id in recent posts, but also actual preview data
            - New Comment
                - After commit to database, numComments is updated in database as well as Redis cache
                - If post is not in Redis cache then do not update
            - New Vote
                - After commit to database, score is updated in database
                - If post/comment is not in Redis cache, then do not update

"""
