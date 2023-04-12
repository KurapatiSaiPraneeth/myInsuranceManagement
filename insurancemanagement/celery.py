from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insurancemanagement.settings')

app = Celery('insurancemanagement')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.update(
    result_backend='amqp://',
    task_serializer='json',
    accept_content=['json'],
    broker_url='amqp://guest:guest@localhost:5672//'
)


app.autodiscover_tasks()
