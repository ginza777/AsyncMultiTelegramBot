from apps.bot.models import TelegramProfile
from django.db import models


class ChatGptUser(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(TelegramProfile, on_delete=models.SET_NULL, verbose_name="Telegram User",unique=True, null=True, blank=True)
    chat_id = models.CharField(max_length=255, verbose_name="Chat ID", null=True, blank=True)
    last_interaction = models.DateTimeField(auto_now=True, verbose_name="Last Interaction")
    first_seen = models.DateTimeField(auto_now_add=True, verbose_name="First Seen")
    curent_dialog_id=models.CharField(max_length=255, verbose_name="Current Dialog ID", null=True, blank=True,default=None)
    current_chat_mode=models.CharField(max_length=255, verbose_name="Current Chat Mode", null=True, blank=True,default="assistant")
    current_model=models.CharField(max_length=255, verbose_name="Current Model", null=True, blank=True)
    n_used_tokens=models.IntegerField(verbose_name="Number of used tokens", null=True, blank=True,default=0)
    n_generated_images=models.IntegerField(verbose_name="Number of generated images", null=True, blank=True,default=0)
    n_transcribed_seconds=models.IntegerField(verbose_name="Number of transcribed seconds", null=True, blank=True,default=0)

    class Meta:
        verbose_name = "ChatGpt User"
        verbose_name_plural = "ChatGpt Users"



