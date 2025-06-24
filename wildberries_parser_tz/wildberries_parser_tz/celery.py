import os

from celery import Celery

from .settings import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wildberries_parser_tz.settings")

app = Celery(
    'wildberries_parser_tz',
    backend=CELERY_RESULT_BACKEND,
    broker=CELERY_BROKER_URL
)
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(
    ['parser.celery_tasks']
)
