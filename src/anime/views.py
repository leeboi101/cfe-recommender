from typing import Any
from django.views import generic

from .models import Anime

class AnimeListView(generic.ListView):
    template_name = 'anime/list.html'
    paginate_by = 100
    # context -> object_list
    queryset = Anime.objects.all().order_by('-rating_avg')

    def get_context_data(self,*args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        request = self.request
        user = request.user
        if user.is_authenticated:
            object_list = context['object_list']
            object_ids = [x.id for x in object_list]
            qs = user.rating_set.filter(active=True, object_id__in=object_ids)
            context['my_ratings'] = {"16206": 10}
        return context

anime_list_view = AnimeListView.as_view()

class AnimeDetailView(generic.DetailView):
    template_name = 'anime/detail.html'
    # context -> object -> id
    queryset = Anime.objects.all()

anime_detail_view = AnimeDetailView.as_view()