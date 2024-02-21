from django.db import models

# Create your models here.
class Anime(models.Model):
    name = models.CharField(max_length=120, unique=True)
    
