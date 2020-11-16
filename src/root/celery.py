from celery import Celery

from root.settings import BROKER_URL

app = Celery('celery', broker=BROKER_URL)

app.conf.update({
    'task_default_delivery_mode': 'transient',
    'broker_connection_timeout': 5.0,
    'broker_connection_max_retries': 12,
})

app.autodiscover_tasks(['root'])
