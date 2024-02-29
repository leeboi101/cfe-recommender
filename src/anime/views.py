from django.views import generic

from .models import Anime

class AnimeListView(generic.ListView):
    template_name = 'anime/list.html'
    paginate_by = 100
    # context -> object_list
    queryset = Anime.objects.all().order_by('-rating_avg')

anime_list_view = AnimeListView.as_view()

class AnimeDetailView(generic.DetailView):
    template_name = 'anime/detail.html'
    # context -> object -> id
    queryset = Anime.objects.all()

anime_detail_view = AnimeDetailView.as_view()