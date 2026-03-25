import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'habit_tracker.settings')

app = Celery('habit_tracker')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks() # Автоматически ищет задачи в приложениях

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
