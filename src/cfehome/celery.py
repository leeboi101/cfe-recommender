import os 


from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cfehome.settings')

app = Celery('cfehome')

# CELERY_
app.config_from_object("django.conf:settings", namespace='CELERY')

app.autodiscover_tasks()



app.conf.beat_schedule= {
    "run_anime_rating_avg_every_30": {
        'task': 'task_calculate_movie_ratings',
        'schedule': 30, #30 minutes
        'kwargs': {"all":True}

    }
}