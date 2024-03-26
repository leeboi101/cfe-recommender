import uuid
import pathlib

from django.db import models
from django.utils import timezone

from . import storages as export_storages

def export_file_handler(instance, filename):
    today = timezone.now().strftime("%y-%m-%d")
    fpath = pathlib.Path(filename)
    ext = fpath.suffix #includes . ex .csv
    dtype = instance.type
    if hasattr(instance, 'id'):
        new_fname = f"{instance.id}{ext}"
    else:
        new_fname = f"{uuid.uuid4}{ext}"
    return f"exports/{dtype}/{today}/{new_fname}"

class ExportDataType(models.TextChoices):
    RATINGS = 'ratings', 'Ratings'
    ANIME = 'anime', 'Anime'

# Create your models here.
class Export(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    file = models.FileField(upload_to=export_file_handler, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=  20, choices=ExportDataType.choices, default=ExportDataType.RATINGS)
    latest = models.BooleanField(default=True)