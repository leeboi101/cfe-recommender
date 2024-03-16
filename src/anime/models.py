import datetime
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Q, F, Sum, Case, When
from ratings.models import Rating
from django.utils import timezone


RATING_CALCULATE_TIME_IN_DAYS = 3

class AnimeQuerySet(models.QuerySet):
    def popular(self, reverse=False):
        ordering = '-score'
        if reverse:
            ordering = 'score'
        return self.order_by(ordering)
    
    def popular_calc(self, reverse=False):
        ordering = '-score'
        if reverse:
            ordering = 'score'
        return self.annotate(score=Sum(
                F('rating_avg')*F('rating_count'),
                output_field=models.FloatField()
            )
        ).order_by(ordering)
    
    def needs_updating(self):
        now = timezone.now()
        days_ago = now - datetime.timedelta(days=RATING_CALCULATE_TIME_IN_DAYS)
        return self.filter(Q(rating_last_updated__isnull=True)|
                           Q(rating_last_updated__lte=days_ago))

class AnimeManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return AnimeQuerySet(self.model, using=self._db)
    
    def by_id_order(self, anime_ids=[]):
        qs = self.get_queryset().filter(id__in=anime_ids)
        maintain_order = Case(*[When(pk=pki, then=idx) for idx, pki in enumerate(anime_ids)])
        return qs.order_by(maintain_order)

    def needs_updating(self):
        return self.get_queryset().needs_updating()


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=True)

    def __str__(self):
        return self.name
    

class Anime(models.Model):
    title = models.CharField(max_length=120, unique=True)
    synopsis = models.TextField()
    start_date = models.DateField(blank=True, null=True, auto_now=False, auto_now_add=False)
    end_date = models.DateField(blank=True, null=True, auto_now=False, auto_now_add=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    ratings = GenericRelation(Rating) #this is a queryset, it's foreign key set.
    rating_last_updated = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    rating_count = models.IntegerField(blank=True, null=True)
    rating_avg = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True) #max it'll be is 10.00, minimum 0.00
    score = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    objects = AnimeManager()
    genre = models.ManyToManyField(Genre, related_name='genre')
    def get_absolute_url(self):
        return f"/anime/{self.id}/"
    def __str__(self):
        if not self.start_date:
            return f"{self.title}"
        return f"{self.title} ({self.start_date.year})"

    def ratings_avg_display(self):
        now = timezone.now()
        if not self.rating_last_updated:
            return self.calculate_rating()
        if self.rating_last_updated > now - datetime.timedelta(days=RATING_CALCULATE_TIME_IN_DAYS):
            return self.rating_avg
        return self.calculate_rating()


    def calculate_ratings_count(self):
        return self.ratings.all().count()

    def calculate_ratings_avg(self):
        return self.ratings.all().avg()
    
    def calculate_rating(self, save=True):
        rating_avg = self.calculate_ratings_avg()
        rating_count = self.calculate_ratings_count()
        self.rating_count = rating_count
        self.rating_avg = rating_avg
        self.rating_last_updated = timezone.now()
        if save:
            self.save()
        return rating_avg
