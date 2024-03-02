from typing import Any
from django.db.models.query import QuerySet
from django.views import generic

from .models import Anime


SORTING_CHOICES = {
    "popular": "-rating_avg",
    "unpopular": "rating_avg",
    "recent": "-start_date",
    "old": "start_date"
}

class AnimeListView(generic.ListView):
    template_name = 'anime/list-view.html'
    paginate_by = 100
    # context -> object_list

    def get_queryset(self):
        request = self.request
        default_sort = request.session.get('anime_sort_order') or 'rating_avg'
        qs = Anime.objects.all().order_by(default_sort)
        request = self.request
        sort = request.GET.get('sort')
        if sort is not None:
            request.session['anime_sort_order'] = sort
            qs = qs.order_by(sort)
        return qs

    def get_template_names(self):
        request = self.request
        if request.htmx:
            return ['anime/snippet/list.html']
        return ['anime/list-view.html']

    def get_context_data(self,*args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        request = self.request
        user = request.user
        context['sorting_choices'] = SORTING_CHOICES
        if user.is_authenticated:
            object_list = context['object_list']
            object_ids = [x.id for x in object_list]
            my_ratings = user.rating_set.anime().as_object_dict(object_ids=object_ids)
            context['my_ratings'] = my_ratings
        return context

anime_list_view = AnimeListView.as_view()

class AnimeDetailView(generic.DetailView):
    template_name = 'anime/detail.html'
    # context -> object -> id
    queryset = Anime.objects.all()

    def get_context_data(self,*args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        request = self.request
        user = request.user
        if user.is_authenticated:
            object = context['object']
            object_ids = [object.id]
            my_ratings = user.rating_set.anime().as_object_dict(object_ids=object_ids)
            context['my_ratings'] = my_ratings
        return context
anime_detail_view = AnimeDetailView.as_view()