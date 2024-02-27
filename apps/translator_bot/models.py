from django.db import models

from apps.bot_main_setup.models import TelegramProfile


class TranslatorUser(models.Model):
    user = models.ForeignKey(
        TelegramProfile, on_delete=models.SET_NULL, verbose_name="Translator User", null=True, blank=True
    )
    native_language = models.CharField(max_length=10, null=True, blank=True, default='uz')
    target_language = models.CharField(max_length=10, null=True, blank=True, default='en')



class TranslatorConversation(models.Model):
    user = models.ForeignKey(TranslatorUser, on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField()
    translated_text = models.TextField()
    source_language = models.CharField(max_length=10, null=True, blank=True)
    target_language = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
