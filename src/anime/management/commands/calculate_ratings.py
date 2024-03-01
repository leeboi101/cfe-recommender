from django.core.management.base import BaseCommand, CommandParser
from django.contrib.auth import get_user_model

from ratings.tasks import task_update_anime_ratings
#from anime.tasks import task_calculate_anime_ratings

User = get_user_model() #custom auth

class Command(BaseCommand):
    def handle(self, *args, **options):
        task_update_anime_ratings()