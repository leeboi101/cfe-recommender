from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.views import generic
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Anime, Watchlist
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404

SORTING_CHOICES = {
    "popular": "popular",
    "unpopular": "unpopular",
    "Top Rated": "-rating_avg",
    "Low Rated": "rating_avg",
    "recent": "-start_date",
    "old": "start_date"
}

class AnimeListView(generic.ListView):
    template_name = 'anime/list-view.html'
    paginate_by = 100
    # context -> object_list

    def get_queryset(self):
        request = self.request
        sort = request.GET.get('sort') or request.session.get('anime_sort_order') or 'popular'
        qs = Anime.objects.all()
        request = self.request
        if sort is not None:
            request.session['anime_sort_order'] = sort
            if sort == 'popular':
                return qs.popular()
            elif sort == 'unpopular':
                return qs.popular(reverse=True)
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

            watchlist_animes = Watchlist.objects.filter(user=user).values_list('anime', flat=True)
            context['watchlist_animes'] = watchlist_animes
            for anime in object_list:
                anime.is_in_watchlist = anime.id in watchlist_animes
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
            watchlist_animes = Watchlist.objects.filter(user=self.request.user).values_list('anime_id', flat=True)
            context['watchlist_animes'] = watchlist_animes
        return context
anime_detail_view = AnimeDetailView.as_view()


class AnimeInfiniteRatingView(AnimeDetailView):
    def get_object(self):
        return Anime.objects.all().order_by("?").first()
    
    def get_template_names(self):
        request = self.request
        if request.htmx:
            return ['anime/snippet/infinite.html']
        return ['anime/infinite-view.html']
    def get_context_data(self, **kwargs):
        context = super(AnimeInfiniteRatingView, self).get_context_data(**kwargs)
        # Assuming you have a method to get the user's watchlist anime IDs:
        if self.request.user.is_authenticated:
            watchlist_animes = Watchlist.objects.filter(user=self.request.user).values_list('anime_id', flat=True)
            context['watchlist_animes'] = watchlist_animes
        return context


anime_infinite_rating_view = AnimeInfiniteRatingView.as_view()



class AnimePopularView(AnimeDetailView):
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['endless_path'] = '/anime/popular/'
        return context

    def get_object(self):
        user = self.request.user
        exclude_ids = []
        if user.is_authenticated:
            exclude_ids = [x.object_id for x in user.rating_set.filter(active=True)]
        anime_id_options = Anime.objects.all().popular().exclude(id__in=exclude_ids).values_list('id', flat=True)[:250]
        return Anime.objects.filter(id__in=anime_id_options).order_by("?").first()
    
    def get_template_names(self):
        request = self.request
        if request.htmx:
            return ['anime/snippet/infinite.html']
        return ['anime/infinite-view.html']


anime_popular_view = AnimePopularView.as_view()

class WatchlistView(LoginRequiredMixin, generic.ListView):
    template_name = 'anime/watchlist.html'

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user).select_related('anime')

    def get_context_data(self,*args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['watchlist'] = self.get_queryset()
        return context
watchlist_view = WatchlistView.as_view() 

@login_required
def add_to_watchlist(request, anime_id):
    user = request.user
    anime = get_object_or_404(Anime, id=anime_id)
    _, created = Watchlist.objects.get_or_create(user=user, anime=anime)

    # Check if it's an AJAX call
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'created': created})

    # For non-AJAX requests, redirect to the previous page or a success page
    redirect_url = request.GET.get('next', reverse('anime:anime_list_view'))
    return HttpResponseRedirect(redirect_url)

@login_required
def remove_from_watchlist(request, anime_id):
    user = request.user
    Watchlist.objects.filter(user=user, anime_id=anime_id).delete()
    return redirect(request.GET.get('next', reverse('anime:watchlist')))