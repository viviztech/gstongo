"""
Celery configuration for GSTONGO.
"""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gstongo.settings')

app = Celery('gstongo')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


# Beat schedule for periodic tasks
app.conf.beat_schedule = {
    # Filing reminder - 1st to 5th of each month
    'filing-reminder-early': {
        'task': 'apps.core.tasks.filing_reminder',
        'schedule': crontab(day_of_month='1-5', hour=9, minute=0),
        'args': (1,),  # Early reminder
    },
    # GSTR-1 filing status check - 10th of each month
    'gstr1-status-check': {
        'task': 'apps.core.tasks.filing_status_check',
        'schedule': crontab(day_of_month='10', hour=10, minute=0),
        'args': ('GSTR1',),
    },
    # GSTR-3B filing status check - 20th of each month
    'gstr3b-status-check': {
        'task': 'apps.core.tasks.filing_status_check',
        'schedule': crontab(day_of_month='20', hour=10, minute=0),
        'args': ('GSTR3B',),
    },
    # Payment reminder - daily at 10 AM for overdue invoices
    'payment-reminder-daily': {
        'task': 'apps.core.tasks.payment_reminder',
        'schedule': crontab(hour=10, minute=0),
    },
    # Generate proforma invoices after filing - daily at 11 AM
    'generate-proforma-invoices': {
        'task': 'apps.core.tasks.generate_proforma_invoices',
        'schedule': crontab(hour=11, minute=0),
    },
    # Update overdue invoices - daily at midnight
    'update-overdue-invoices': {
        'task': 'apps.core.tasks.update_overdue_invoices',
        'schedule': crontab(hour=0, minute=0),
    },
    # Monthly report generation - 1st of each month at 6 AM
    'monthly-report': {
        'task': 'apps.core.tasks.generate_monthly_report',
        'schedule': crontab(day_of_month='1', hour=6, minute=0),
    },
}

app.conf.timezone = 'Asia/Kolkata'


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery."""
    print(f'Request: {self.request!r}')
