from celery import shared_task
from anime.models import Anime
from anime.models import AnimeQuerySet
from profiles import utils as profiles_utils
from . import utils as ml_utils

@shared_task
def train_surprise_model_task():
    ml_utils.train_surprise_model()


@shared_task
def batch_user_prediction_task(start_page=0, offset=250, max_pages=1000):
    model = ml_utils.load_model()
    end_page = start_page + offset
    recent_user_ids = profiles_utils.get_recent_users()
    anime_ids = Anime.objects.all().popular().values_list('id', flat=True)[start_page:end_page]
    for anime_id in anime_ids:
        for u in recent_user_ids:
            pred = model.predict(uid=u, iid=anime_id).est
            print(u, anime_id, pred)
    if end_page < max_pages:
        return batch_user_prediction_task(start_page=end_page-1)