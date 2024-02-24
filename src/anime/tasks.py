

from.models import Anime

def task_calculate_movie_ratings(all=False, count=None):
    qs = Anime.objects.needs_updating()
    if all:
        qs = Anime.objects.all()
    qs = qs.order_by('rating_last_updated')
    if isinstance(count, int):
        qs = qs[:count]

    for obj in qs:
        obj.calculate_rating(save=True)

