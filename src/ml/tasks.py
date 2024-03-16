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
from django.db.models import Count
@shared_task
def train_surprise_model_task():
    ml_utils.train_surprise_model()

@shared_task
def batch_users_prediction_task(users_ids=None, start_page=0, offset=10, max_pages=1000):
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


def batch_single_user_prediction_task(user_id=1, start_page=0, offset=10, max_pages=1000):
    return batch_users_prediction_task(users_ids=[user_id], start_page=start_page, offset=offset, max_pages=max_pages)

# User = get_user_model()


# from django.contrib.auth import get_user_model
# from django.db.models import Count, Exists, OuterRef
# from django.apps import apps


# Rating = apps.get_model('ratings', 'Rating')  # Make sure this is correctly referenced

# @shared_task
# def check_users_with_ratings_and_suggestions(target_suggestions=10):
#     # Check for users who have rated at least one anime
#     users_with_at_least_one_rating = User.objects.annotate(
#         has_rated=Exists(
#             Rating.objects.filter(user_id=OuterRef('id'))
#         )
#     ).filter(has_rated=True)

#     # Within those users, annotate and count suggestions as before
#     users_annotation = users_with_at_least_one_rating.annotate(
#         suggestions_count=Count('suggestion')  # Ensure 'suggestion' matches your actual relation or related_name
#     )

#     # Collect user IDs not matching the exact target_suggestions, but have rated
#     users_not_matching_ids = users_annotation.exclude(
#         suggestions_count=target_suggestions
#     ).values_list('id', flat=True)

#     # For logging or debugging
#     exact_match_count = users_annotation.filter(suggestions_count=target_suggestions).count()
#     not_match_count = len(users_not_matching_ids)
#     print(f"Users who have rated and have exactly {target_suggestions} suggestions: {exact_match_count}")
#     print(f"Users who have rated and don't have exactly {target_suggestions} suggestions: {not_match_count}")

#     # Return IDs of users who have rated but do not match the suggestions criteria
#     return list(users_not_matching_ids)


# def get_users_with_fewer_than_target_suggestions(target=10):
#     """Returns a QuerySet of users with fewer than 'target' suggestions."""
#     User = get_user_model()
#     users_with_fewer_suggestions = User.objects.annotate(
#         suggestions_count=Count('suggestion')
#     ).filter(
#         suggestions_count__lt=target
#     )
#     return users_with_fewer_suggestions

# def get_users_with_fewer_than_target_suggestions(target=253):
#     User = get_user_model()
#     return User.objects.annotate(
#         suggestions_count=Count('suggestion')  # Make sure 'suggestions' is the correct relation name or related_name from User to Suggestion
#     ).filter(suggestions_count__lt=target)


# def get_users_with_fewer_than_target_suggestions(target=253):
#     User = get_user_model()
#     return User.objects.annotate(
#         suggestions_count=Count('suggestion')  # Make sure 'suggestions' is the correct relation name or related_name from User to Suggestion
#     ).filter(suggestions_count__lt=target)

# @shared_task
# def batch_users_prediction_task_modified(target_suggestions=253, start_page=0, offset=253, max_pages=1000):
#     model = ml_utils.load_model()
#     Suggestion = apps.get_model('suggestions', 'Suggestion')
#     ctype = ContentType.objects.get(app_label='anime', model='anime')

#     users_ids = list(get_users_with_fewer_than_target_suggestions(target=target_suggestions).values_list('id', flat=True))

#     # This might be a redundant check if get_users_with_fewer_than_target_suggestions always returns a QuerySet
#     if not users_ids:
#         users_ids = list(profiles_utils.get_recent_users().values_list('id', flat=True))
    
#     anime_ids = Anime.objects.all().popular().values_list('id', flat=True)[start_page:start_page+offset]
#     recently_suggested = Suggestion.objects.get_recently_suggested(anime_ids, users_ids)
#     new_suggestion = []

#     for anime_id in anime_ids:
#         users_done = recently_suggested.get(f"{anime_id}") or []

#         for u in users_ids:
#             if u in users_done:
#                 #print(anime_id, 'is done for', u, 'user')
#                 continue
#             pred = model.predict(uid=u, iid=anime_id).est
#             data = {
#                 'user_id': u,
#                 'object_id': anime_id,
#                 'value': pred,
#                 'content_type': ctype,
#             }
#             new_suggestion.append(Suggestion(**data))
    
#     Suggestion.objects.bulk_create(new_suggestion, ignore_conflicts=True)
    
#     end_page = start_page + offset
#     if end_page < max_pages:
#         batch_users_prediction_task_modified.delay(target_suggestions=target_suggestions, start_page=end_page, offset=offset, max_pages=max_pages)