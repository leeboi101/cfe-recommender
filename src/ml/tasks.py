from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from celery import shared_task
from anime.models import Anime
from profiles import utils as profiles_utils
from . import utils as ml_utils
from django.contrib.auth import get_user_model
from django.db.models import Count
@shared_task
def train_surprise_model_task():
    ml_utils.train_surprise_model()

@shared_task
def batch_users_prediction_task(users_ids=None, start_page=0, offset=200, max_pages=1000):
    model = ml_utils.load_model()
    Suggestion = apps.get_model('suggestions', 'Suggestion')
    ctype = ContentType.objects.get(app_label='anime', model='anime')
    end_page = start_page + offset

    if users_ids is None:
        users_ids = profiles_utils.get_recent_users()
    anime_ids = Anime.objects.all().popular().values_list('id', flat=True)[start_page:end_page]
    recently_suggested = Suggestion.objects.get_recently_suggested(anime_ids,users_ids)
    #print(recently_suggested)
    new_suggestion = []
    if not anime_ids.exists():
        return
    for anime_id in anime_ids:
        users_done = recently_suggested.get(f"{anime_id}") or []

        for u in users_ids:
            if u in users_done:
                    #print(anime_id, 'is done for', u, 'user')
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
        return batch_users_prediction_task(users_ids=users_ids, start_page=end_page, offset=offset, max_pages=max_pages)



def batch_single_user_prediction_task(user_id=1, start_page=0, offset=10, max_pages=1000):
    return batch_users_prediction_task(users_ids=[user_id], start_page=start_page, offset=offset, max_pages=max_pages)

### The section below handles the missed out id's who have less than a certain amount of 
### suggestios. The aim is to grab those id's and then using that, run a modified task that'll
### go through and provide those suggestions to those specific users.

def get_users_with_fewer_than_target_suggestions(target=50):
    User = get_user_model()
    return User.objects.annotate(
        suggestions_count=Count('suggestion')  # Make sure 'suggestions' is the correct relation name or related_name from User to Suggestion
    ).filter(suggestions_count__lt=target)

@shared_task
def batch_users_prediction_task_modified(target_suggestions=10, start_page=0, offset=10, max_pages=1000):
    model = ml_utils.load_model()
    Suggestion = apps.get_model('suggestions', 'Suggestion')
    ctype = ContentType.objects.get(app_label='anime', model='anime')

    users_ids = list(get_users_with_fewer_than_target_suggestions(target=target_suggestions).values_list('id', flat=True))

    # This might be a redundant check if get_users_with_fewer_than_target_suggestions always returns a QuerySet
    if not users_ids:
        users_ids = list(profiles_utils.get_recent_users().values_list('id', flat=True))
    
    anime_ids = Anime.objects.all().popular().values_list('id', flat=True)[start_page:start_page+offset]
    recently_suggested = Suggestion.objects.get_recently_suggested(anime_ids, users_ids)
    new_suggestion = []

    for anime_id in anime_ids:
        users_done = recently_suggested.get(f"{anime_id}") or []

        for u in users_ids:
            if u in users_done:
                #print(anime_id, 'is done for', u, 'user')
                continue
            pred = model.predict(uid=u, iid=anime_id).est
            data = {
                'user_id': u,
                'object_id': anime_id,
                'value': pred,
                'content_type': ctype,
            }
            new_suggestion.append(Suggestion(**data))
    
    Suggestion.objects.bulk_create(new_suggestion, ignore_conflicts=True)
    
    end_page = start_page + offset
    if end_page < max_pages:
        batch_users_prediction_task_modified.delay(target_suggestions=target_suggestions, start_page=end_page, offset=offset, max_pages=max_pages)