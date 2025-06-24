#!/bin/bash

if grep -q $'\r' "$0"; then
    echo "Fixing CRLF line endings in $0..."
    sed -i 's/\r$//' "$0"
    echo "Restarting script..."
    exec "$0" "$@"
    exit 0
fi

set -o errexit
set -o pipefail
set -o nounset

postgres_ready() {
python << END
import sys

import psycopg2

try:
    psycopg2.connect(
        dbname="${DB_POSTGRESQL_NAME}",
        user="${DB_POSTGRESQL_USER}",
        password="${DB_POSTGRESQL_PASSWORD}",
        host="${DB_POSTGRESQL_HOST}",
        port="${DB_POSTGRESQL_PORT}",
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)

END
}

wait_for_postgres() {
    until postgres_ready; do
        >&2 echo 'Waiting for PostgreSQL to become available...'
        sleep 2
    done
    >&2 echo 'PostgreSQL is available'
}


wait_for_redis_celery() {
    until redis-cli -h redis_celery -p 6379 --no-auth-warning -a "$REDIS_CELERY_PASSWORD" ping | grep -q PONG; do
        >&2 echo "Waiting for Redis_Celery to become available..."
        sleep 2
    done
    >&2 echo "Redis_Celery is available!"
}

wait_for_postgres
wait_for_redis_celery

echo "Database migrations..."
python manage.py makemigrations
python manage.py migrate

mkdir -p /app/staticfiles
mkdir -p /app/mediafiles

mkdir -p /app/logs
chmod 755 /app/logs

mkdir -p /app/logs/django
chmod 755 /app/logs/django

echo "Static files collection..."
python manage.py collectstatic --noinput

echo "Launching server..."
exec "$@"