#!/bin/sh

#source venv/bin/activate

# If running in development with database container, then ensure connection is ready

if [ $FLASK_ENV = "development" ]; then
  i=0
  echo "Waiting for rabbitmq @ host:$RABBITMQ_HOST - port:$RABBITMQ_PORT"
  while ! nc -z $RABBITMQ_HOST $RABBITMQ_PORT; do
      sleep 5
      i=$((i+1))
      if [[ $i -gt 3 ]]; then
        echo "Could not connect after 3 retries. Exiting."
        exit 1
      fi
  done
  echo "RabbitMQ started."
fi

if [ $FLASK_ENV = "development" ]; then
  echo "Waiting for postgres..."
  i=0
  while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 2
      i=$((i+1))
      if [[ $i -gt 3 ]]; then
        echo "Could not connect after 3 retries. Exiting."
      fi
  done
  echo "Postgres started."
fi

echo "Running schema updates..."

flask db upgrade

echo "Schema update successful."

if [ -z "$@" ]; then
  echo "[./run.sh] No command received. Running default gunicorn server."
  exec gunicorn -b :5000 --access-logfile - --error-logfile - app:app
else
  echo "[./run.sh] Received command. Running $@"
  exec "$@"
fi
