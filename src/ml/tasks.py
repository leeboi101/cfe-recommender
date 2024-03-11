from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from celery import shared_task
from anime.models import Anime
from anime.models import AnimeQuerySet
from profiles import utils as profiles_utils
from . import utils as ml_utils
from django.contrib.auth import get_user_model
from celery import shared_task
from ratings.models import Rating  # Import your Rating model correctly

@shared_task
def train_surprise_model_task():
    ml_utils.train_surprise_model()

@shared_task
def batch_users_prediction_task(users_ids=None, start_page=0, offset=253, max_pages=1000):
    model = ml_utils.load_model()
    Suggestion = apps.get_model('suggestions', 'Suggestion')
    ctype = ContentType.objects.get(app_label='anime', model='anime')
    end_page = start_page + offset

    if users_ids is None:
        users_ids = profiles_utils.get_recent_users()
    anime_ids = Anime.objects.all().popular().values_list('id', flat=True)[start_page:end_page]
    recently_suggested = Suggestion.objects.get_recently_suggested(anime_ids,users_ids)
    new_suggestion = []

    for anime_id in anime_ids:
        users_done = recently_suggested.get(f"{anime_id}") or []

        for u in users_ids:
            if u in users_done:
                    print(anime_id, 'is done for', u, 'user')
                    continue
            pred = model.predict(uid=u, iid=anime_id).est
            data = {
                'user_id':u,
                'object_id': anime_id,
                'value': pred,
                'content_type': ctype,


            }
            new_suggestion.append(
                Suggestion(**data)
            )
    Suggestion.objects.bulk_create(new_suggestion, ignore_conflicts=True)
    if end_page < max_pages:
        return batch_users_prediction_task(start_page=end_page-1)


def batch_single_user_prediction_task(user_id=1, start_page=0, offset=253, max_pages=1000):
    return batch_users_prediction_task(users_ids=[user_id], start_page=start_page, offset=offset, max_pages=max_pages)
User = get_user_model()

@shared_task
def check_suggestions_per_user(target_suggestions=253):
    Suggestion = apps.get_model('suggestions', 'Suggestion')

    # Annotate each user with the count of their suggestions
    users_annotation = User.objects.annotate(suggestions_count=Count('suggestion'))

    # Count users with exactly target_suggestions suggestions
    exact_match_count = users_annotation.filter(suggestions_count=target_suggestions).count()

    # Count users with less or more than target_suggestions suggestions
    not_match_count = users_annotation.exclude(suggestions_count=target_suggestions).count()

    print(f"Users with exactly {target_suggestions} suggestions: {exact_match_count}")
    print(f"Users without exactly {target_suggestions} suggestions: {not_match_count}")

    return exact_match_count, not_match_count