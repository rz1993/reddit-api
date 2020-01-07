#!/bin/sh

#source venv/bin/activate

# If running in development with database container, then ensure connection is ready
if [ $FLASK_ENV = "development" ]; then
  echo "Waiting for postgres..."
  while ! nc -z reddit_db 5432; do
      sleep 2
  done
  echo "Postgres started."
fi

echo "Running schema updates..."

flask db upgrade

echo "Schema update successful."

exec gunicorn -b :5000 --access-logfile - --error-logfile - app:app
