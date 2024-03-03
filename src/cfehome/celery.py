import os


from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cfehome.settings')

app = Celery('cfehome')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()



app.conf.beat_schedule= {
   "run_anime_rating_avg_every_30": {
      'task': 'task_update_anime_ratings',
      'schedule': 60 * 30, #30 minutes
    }
}
app.conf.beat_schedule= {
   "run_rating_export_every_60": {
      'task': 'export_rating_dataset',
      'schedule': 60 * 60, #30 minutes
    }
}