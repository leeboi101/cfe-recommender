from django.apps import apps
from celery import shared_task
from django.db.models import Window, F
from django.db.models.functions import DenseRank

@shared_task
def update_anime_position_embedding_idx():
    Anime = apps.get_model('anime','Anime')
    qs = Anime.objects.all().annotate(
        new_idx=Window(
            expression=DenseRank(),
            order_by=[F('id').asc()]
        )
    ).annotate(final_idx = F('new_idx') - 1)
    updated = 0
    for obj in qs:
        if obj.final_idx != obj.idx:
            updated += 1
            obj.idx = obj.final_idx
            obj.save()
    print("Updated: {updated} anime idx fields")

### Purpose of this task is to provide new ids based off the posiitonings that the objects are in.
### We call uponse DenseRank which allows us to set up an Expression that can ensure that it reads
### all the idx and compares it to the positions and based off that, assign it a similar value. 

### the second annotation allows us the program to...
### The For loop...