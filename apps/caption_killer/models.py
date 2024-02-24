from django.db import models
from django.core.exceptions import ValidationError


# Create your models here.


class Channel(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    channel_id = models.CharField(max_length=200, null=True, blank=True)
    channel_sign =models.TextField()

    def __str__(self):
        return self.name


class Keyword(models.Model):
    text = models.TextField()
    channel = models.ForeignKey(Channel, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.text

    class Meta:
        unique_together = ('text', 'channel')
        # app_label = 'setting_ads'

