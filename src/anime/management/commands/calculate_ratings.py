from django.core.management.base import BaseCommand, CommandParser
from django.contrib.auth import get_user_model

from anime.tasks import task_calculate_anime_ratings

User = get_user_model() #custom auth

class Command(BaseCommand):
    def add_arguments(self, parser):
       parser.add_argument("count", nargs='?', default=1000, type=int)
       parser.add_argument("--show-all", action='store_true', default=False)

    def handle(self, *args, **options):
        count = options.get('count')
        all = options.get('all')
        task_calculate_anime_ratings(all=all, count=count)