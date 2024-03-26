import csv
import tempfile
from django.core.files.base import File
from django.db.models import F
from django.contrib.contenttypes.models import ContentType

from ratings.models import Rating
from anime.models import Anime

from .models import Export, ExportDataType
from io import BytesIO
from django.core.files.base import ContentFile

def export_dataset(dataset, fname='dataset.csv', type=ExportDataType.RATINGS):
    with tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', newline='') as temp_f:
        try:
            keys = dataset[0].keys()
        except IndexError:
            return
        dict_writer = csv.DictWriter(temp_f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(dataset)
        temp_f.seek(0)  # Go to the top of the file
        
        # Read content from the temporary file and create a ContentFile for Django
        content = temp_f.read().encode('utf-8')
        content_file = ContentFile(content, name=fname)
        
        # Write Export model
        obj = Export.objects.create(type=type)
        obj.file.save(fname, content_file)


def generate_rating_dataset(app_label='anime', model='anime', to_csv=True):
    ctype = ContentType.objects.get(app_label=app_label, model=model)
    qs = Rating.objects.filter(active=True, content_type=ctype)
    qs = qs.annotate(userId=F('user_id'),animeId=F("object_id"), rating=F("value"))
    dataset = qs.values('userId','animeId','rating')
    if to_csv:
        export_dataset(dataset=dataset, fname='rating.csv', type=ExportDataType.RATINGS)
    return dataset

def generate_anime_dataset(to_csv=True):
    qs = Anime.objects.all()
    qs = qs.annotate(animeId=F('id'),animeIdx=F("idx"))
    dataset = qs.values('animeIdx','animeId','title', 'start_date', 'rating_count', 'rating_avg')
    if to_csv:
        export_dataset(dataset=dataset, fname='anime.csv', type=ExportDataType.ANIME)
    return dataset
