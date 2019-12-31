#!/bin/sh

#source venv/bin/activate
echo "Waiting for postgres..."

while ! nc -z reddit_db 5432; do
    sleep 2
done

echo "Postgres started."

echo "Running schema updates..."

flask db upgrade

echo "Schema update successful."

exec gunicorn -b :5000 --access-logfile - --error-logfile - app:app
