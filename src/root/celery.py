from celery import Celery

from root.settings import BROKER_URL, CELERY_WORKERS

app = Celery('celery', broker=BROKER_URL)

app.conf.update({
    'task_default_delivery_mode': 'transient',
    'broker_connection_timeout': 5.0,
    'broker_connection_max_retries': 12,
    'worker_concurrency': CELERY_WORKERS,
})

app.autodiscover_tasks(['root'])
