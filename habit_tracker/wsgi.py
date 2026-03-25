import os
from django.core.wsgi import get_wsgi_application
from habit_tracker.celery import app

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'habit_tracker.settings')

application = get_wsgi_application()
app.config_from_object('django.conf:settings', namespace='CELERY') # Добавить
app.autodiscover_tasks() # Добавить