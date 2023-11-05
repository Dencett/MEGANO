import os
from celery import Celery

# commands
# celery -A config worker --loglevel=INFO
# celery -A config flower --loglevel=INFO

# Celery https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html#django-first-steps
# Real Python https://realpython.com/asynchronous-tasks-with-django-and-celery/


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
