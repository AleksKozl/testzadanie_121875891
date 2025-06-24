#!/bin/bash

set -o errexit
set -o nounset

echo "Starting Celery Worker..."

rm -f ./celery_worker.pid
echo "Removed existing PID file: celery_worker.pid"

mkdir -p /app/logs/celery_worker
chmod 755 /app/logs/celery_worker
echo "Log directory set up: app/logs/celery_worker"

celery -A wildberries_parser_tz.celery worker -l INFO >> /app/logs/celery_worker/celery-worker.log 2>&1

echo "Celery Worker started, check logs."
