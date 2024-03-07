import random
import time
import datetime

from celery import shared_task
from django.db.models import Avg, Count
from anime.models import Anime
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from anime.models import Anime
from .models import Rating, RatingChoice


User = get_user_model()

@shared_task(name='generate_fake_reviews')
def generate_fake_reviews(count=100, users=10, null_avg=False):
    user_s = User.objects.first() #first user
    user_e = User.objects.last() #last user
    random_user_ids = random.sample(range(user_s.id, user_e.id), users)
    users = User.objects.filter(id__in=random_user_ids)
    animes = Anime.objects.all().order_by("?")[:count]
    if null_avg:
        animes = Anime.objects.filter(rating_avg__isnull=True).order_by("?")[:count]
    n_ratings = animes.count()
    rating_choices = [x for x in RatingChoice.values if x is not None]
    user_ratings = [random.choice(rating_choices) for _ in range(0, n_ratings)]

    new_ratings = []
    for anime in animes:
        rating_obj = Rating.objects.create(
            content_object = anime,
            value = user_ratings.pop(),
            user = random.choice(users)
        )
        new_ratings.append(rating_obj.id)
    return new_ratings

@shared_task(name='task_update_anime_ratings')
def task_update_anime_ratings(object_id=None):
    start_time = time.time()
    ctype = ContentType.objects.get_for_model(Anime)
    rating_qs = Rating.objects.filter(content_type=ctype)
    agg_ratings = Rating.objects.filter(content_type=ctype).values('object_id').annotate(average=Avg('value'), count=Count('object_id'))
    if object_id is not None:
        rating_qs = rating_qs.filter(object_id=object_id)
    agg_ratings = Rating.objects.filter(content_type=ctype).values('object_id').annotate(average=Avg('value'), count=Count('object_id'))
    for agg_rate in agg_ratings:
        object_id = agg_rate['object_id']
        rating_avg = agg_rate['average']
        rating_count = agg_rate['count']
        score = rating_avg * rating_count
        qs = Anime.objects.filter(id=object_id)
        qs.update(
            rating_avg=rating_avg,
            rating_count=rating_count,
            score=score,
            rating_last_updated=timezone.now()
        )
    total_time = time.time() - start_time
    delta = datetime.timedelta(seconds=int(total_time))
    print(f"Rating update took {delta} {total_time}s")