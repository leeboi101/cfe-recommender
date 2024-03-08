from django.apps import apps
from django.db import models
from django.conf import settings
from django.db.models import Avg
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.utils import timezone
User = settings.AUTH_USER_MODEL #'auth.User'


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

    class Meta:
        ordering = ['-timestamps']

