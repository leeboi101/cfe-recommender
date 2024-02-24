from django.contrib import admin

# Register your models here.
from .models import Anime

class AnimeAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'rating_count', 'rating_avg', 'rating_last_updated']
    readonly_fields = ['rating_avg', 'rating_count', 'ratings_avg_display']

admin.site.register(Anime, AnimeAdmin)