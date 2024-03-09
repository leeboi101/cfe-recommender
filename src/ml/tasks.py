from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from celery import shared_task
from anime.models import Anime
from anime.models import AnimeQuerySet
from profiles import utils as profiles_utils
from . import utils as ml_utils

@shared_task
def train_surprise_model_task():
    ml_utils.train_surprise_model()


# @shared_task
# def batch_users_prediction_task(users_ids=None, start_page=0, offset=250, max_pages=1000):
#     model = ml_utils.load_model()
#     suggestion = apps.get_model('suggestions', 'Suggestion')
#     ctype = ContentType.objects.get(app_label='anime', model='anime')
#     end_page = start_page + offset
#     if users_ids is None:
#         users_ids = profiles_utils.get_recent_users()
#     anime_ids = Anime.objects.all().popular().values_list('id', flat=True)[start_page:end_page]
#     new_suggestion = []
#     for anime_id in anime_ids:
#         for u in users_ids:
#             pred = model.predict(uid=u, iid=anime_id).est
#             data = {
#                 'user_id':u,
#                 'object_id': anime_id,
#                 'value': pred,
#                 'content_type': ctype,


#             }
#             new_suggestion.append(
#                 suggestion(**data)
#             )
#     suggestion.objects.bulk_create(new_suggestion, ignore_conflicts=True)
#     if end_page < max_pages:
#         return batch_users_prediction_task(start_page=end_page-1)


# 
@shared_task
def batch_users_prediction_task(users_ids=None, start_page=0, offset=250, max_pages=1000, batch_size=500):
    model = ml_utils.load_model()
    Suggestion = apps.get_model('suggestions', 'Suggestion')
    ctype = ContentType.objects.get(app_label='anime', model='anime')
    
    if users_ids is None:
        users_ids = profiles_utils.get_recent_users()

    total_anime_ids = Anime.objects.all().popular().count()
    max_pages = min(max_pages, (total_anime_ids // offset) + 1)

    for page_num in range(start_page, max_pages):
        start_index = page_num * offset
        end_index = start_index + offset
        anime_ids = Anime.objects.all().popular().values_list('id', flat=True)[start_index:end_index]

        new_suggestions = []
        for anime_id in anime_ids:
            for user_id in users_ids:
                pred = model.predict(uid=user_id, iid=anime_id).est
                # Check if a suggestion for this user and anime already exists
                exists = Suggestion.objects.filter(user_id=user_id, object_id=anime_id).exists()
                if not exists:
                    data = {
                        'user_id': user_id,
                        'object_id': anime_id,
                        'value': pred,
                        'content_type': ctype,
                    }
                    new_suggestions.append(Suggestion(**data))

                # Insert in batches to avoid excessive memory usage
                if len(new_suggestions) >= batch_size:
                    Suggestion.objects.bulk_create(new_suggestions, ignore_conflicts=True)
                    new_suggestions = []

        # Insert any remaining suggestions
        if new_suggestions:
            Suggestion.objects.bulk_create(new_suggestions, ignore_conflicts=True)


def batch_single_user_prediction_task(user_id=1, start_page=0, offset=250, max_pages=1000):
    return batch_users_prediction_task(users_ids=[user_id], start_page=start_page, offset=offset, max_pages=max_pages)
