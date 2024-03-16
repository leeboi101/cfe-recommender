from django.core.management.base import BaseCommand, CommandParser
from django.contrib.auth import get_user_model

from cfehome import utils as cfehome_utils
from anime.models import Anime
from anime.models import Genre
User = get_user_model() #custom auth

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("count", nargs='?', default=10, type=int)
        parser.add_argument("--genre", action='store_true', default=False)
        parser.add_argument("--atog", action='store_true', default=False)
        parser.add_argument("--show-total", action='store_true', default=False)
    def handle(self,*args,**options):
        count = options.get('count')
        show_total = options.get('show_total')
        load_genre = options.get('genre')
        addtogenre = options.get('atog')
        if addtogenre:
            anime = cfehome_utils.create_or_update_anime_with_genres(limit=count)
            print(f'Updated : {anime}')
        if load_genre:
            genre_dataset = cfehome_utils.load_genre_data(limit=count)
            genre_new = [Genre(**x) for x in genre_dataset]
            genres_bulk = Genre.objects.bulk_create(genre_new, ignore_conflicts=True)
            print(f"New Animes: {len(genres_bulk)}")
            if show_total:
                print(f"Total Animes: {Genre.objects.count()}")