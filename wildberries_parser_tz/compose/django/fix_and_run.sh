#!/bin/bash

SCRIPTS=(
    "/app/compose/django/start_django.sh"
    "/app/compose/celery/start_celery_worker.sh"
)

for script in "${SCRIPTS[@]}"; do
    if grep -q $'\r' "$script"; then
        echo "Fixing CRLF line endings in $script..."
        sed -i 's/\r$//' "$script"
    fi
done

chmod +x /app/compose/django/start_django.sh
exec "/app/compose/django/start_django.sh" "$@"