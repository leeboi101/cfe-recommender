from celery import shared_task

from.models import Anime

@shared_task(name='task_calculate_movie_ratings')
def task_calculate_movie_ratings(all=False, count=None):
    '''
    def task_calculate_movie_ratings(all=False, count=None)
    #these are celery tasks
    def task_calculate_movie_ratings.delay(all=False, count=None)
    def task_calculate_movie_ratings.apply_async(kwargs={"all":False, "count":12}, countdown=30)
    '''    
    qs = Anime.objects.needs_updating()
    if all:
        qs = Anime.objects.all()
    qs = qs.order_by('rating_last_updated')
    if isinstance(count, int):
        qs = qs[:count]

    for obj in qs:
        obj.calculate_rating(save=True)
