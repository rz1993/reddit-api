# Reddit API

[![Build Status](https://travis-ci.org/rz1993/reddit-api.svg?branch=master)](https://travis-ci.org/rz1993/reddit-api)

An example Reddit backend implemented with Flask, Postgres, Redis and RabbitMQ.

## About

Based on the real [Reddit API](https://github.com/reddit-archive/reddit), this is a simplified monolithic clone which contains advanced features such as:

1. Write-through caching
2. Listings (most recent posts for a subreddit or a user feed)
3. Asynchronous Processing (mostly to populate caches, but can easily be extended)

Technologies that were used:

* Flask (Web Framework)
* Postgres (Database)
* Redis (Caching and Denormalized Views)
* RabbitMQ (Asynchronous Event Processing)
* ElasticSearch (Full Text Search)
* Gunicorn (Web Server)
* Docker and Docker-Compose (Containerization)

## Quickstart

Since this application is dependent on external systems, instances of dependencies like Postgres, Redis and RabbitMQ must be running before this app can run. To quickly spin up a complete development environment, you can use docker-compose like so:

```
docker-compose -f compose/docker-compose.yml up -d --build
```

To run tests (although test suite needs some work), can run:

```
docker-compose -f compose/docker-compose.yml exec app python -m pytest
```

## Future Updates

Some features I would eventually like to build are:

* Ranking Posts
* Pagination
* Central Logging
* Authorization/User Roles
