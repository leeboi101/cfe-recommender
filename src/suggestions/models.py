
from django.db import models
from django.conf import settings
from django.db.models import F
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


User = settings.AUTH_USER_MODEL #'auth.User'


class SuggestionManager(models.Manager):
    def get_recently_suggested(self, anime_ids=[], users_ids=[], days_ago=7):
        data = {}
        ctype = ContentType.objects.get(app_label='anime', model='anime')
        dataset = self.get_queryset().filter(content_type=ctype, object_id__in=anime_ids,user_id__in=users_ids).annotate(anime_uid=F('object_id'),uid=F('user_id')).values('anime_uid','uid')
        for d in dataset:
            print(d)
            anime_id = str(d.get('anime_uid'))
            user_id = d.get('uid')
            if anime_id in data:
                data[anime_id].append(user_id)
            else:
                data[anime_id] = [user_id]
        return data


class Suggestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.FloatField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField() #won't work if you have uuid as PK.
    content_object = GenericForeignKey("content_type", "object_id")
    timestamps = models.DateTimeField(auto_now_add=True)

# when ratings occur after a suggestion
    ratin_value = models.FloatField(null=True, blank=True)
    did_rate = models.BooleanField(default=False)
    did_rate_timestamp = models.DateTimeField(auto_now_add=False, auto_now=False,null=True, blank=True )
    objects = SuggestionManager()


    class Meta:
        ordering = ['-timestamps']

