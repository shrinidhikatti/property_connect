import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

app = Celery('propconnect')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'expire-old-listings': {
        'task': 'notifications.tasks.expire_listings',
        'schedule': crontab(hour=2, minute=0),
    },
    'escalate-stale-verifications': {
        'task': 'notifications.tasks.escalate_stale_verifications',
        'schedule': crontab(hour=9, minute=0),
    },
    'expire-subscriptions': {
        'task': 'notifications.tasks.expire_subscriptions',
        'schedule': crontab(hour=0, minute=0),
    },
    'send-renewal-reminders': {
        'task': 'notifications.tasks.send_renewal_reminders',
        'schedule': crontab(hour=10, minute=0),
    },
}
