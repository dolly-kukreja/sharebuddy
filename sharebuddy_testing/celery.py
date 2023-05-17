import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sharebuddy_testing.settings")
app = Celery("sharebuddy_testing")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
