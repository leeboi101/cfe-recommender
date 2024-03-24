from django.contrib import admin

# Register your models here.
from .models import Anime,Genre

class AnimeAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'rating_count', 'rating_avg', 'rating_last_updated']
    readonly_fields = ['rating_avg', 'rating_count', 'ratings_avg_display']
    search_fields = ['id','title']

admin.site.register(Anime, AnimeAdmin)

admin.site.register(Genre, )