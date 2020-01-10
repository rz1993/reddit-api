from elasticsearch_dsl import Document, Date, Keyword, Integer, Text


class Comment(Document):
    author_id = Integer()
    thread_id = Integer()

    body = Text(analyzer='snowball')
    createdAt = Date()

    class Index:
        name = 'comments'
        settings = {
            'number_of_shards': 1
        }


class Thread(Document):
    author_id = Integer()
    subreddit_id = Integer()
    body = Text(analyzer='snowball')
    description = Text(analyzer='snowball')
    title = Text(analyzer='snowball')
    createdAt = Date()


    class Index:
        name = 'threads'
        settings = {
            'number_of_shards': 1
        }
