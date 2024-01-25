from django.db import models
import uuid
from apps.bot.models import TelegramProfile

class ChatGptUser(models.Model):
    AVAILABLE_TEXT_MODELS_CHOICES = [
        ("gpt-3.5-turbo", "GPT-3.5 Turbo"),
        ("gpt-3.5-turbo-16k", "GPT-3.5 Turbo 16k"),
        ("gpt-4-1106-preview", "GPT-4 1106 Preview"),
        ("gpt-4", "GPT-4"),
        ("text-davinci-003", "Text Davinci 003"),
    ]

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(TelegramProfile, on_delete=models.SET_NULL, verbose_name="Telegram User", null=True, blank=True)
    chat_id = models.BigIntegerField(null=True, blank=True)
    last_interaction = models.DateTimeField(auto_now=True, null=True, blank=True)
    first_seen = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    current_dialog_id = models.UUIDField(default=None, null=True, blank=True)
    current_chat_mode = models.CharField(max_length=255, default="assistant")
    current_model = models.CharField(max_length=255, choices=AVAILABLE_TEXT_MODELS_CHOICES, default=AVAILABLE_TEXT_MODELS_CHOICES[0][0])
    n_used_tokens = models.JSONField(default=dict, null=True, blank=True)
    n_generated_images = models.IntegerField(default=0, null=True, blank=True)
    n_transcribed_seconds = models.FloatField(default=0.0, null=True, blank=True)

    class Meta:
        verbose_name = "ChatGpt User"
        verbose_name_plural = "ChatGpt Users"


class Dialog(models.Model):
    AVAILABLE_TEXT_MODELS_CHOICES = [
        ("gpt-3.5-turbo", "GPT-3.5 Turbo"),
        ("gpt-3.5-turbo-16k", "GPT-3.5 Turbo 16k"),
        ("gpt-4-1106-preview", "GPT-4 1106 Preview"),
        ("gpt-4", "GPT-4"),
        ("text-davinci-003", "Text Davinci 003"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(ChatGptUser, on_delete=models.CASCADE, verbose_name="ChatGpt User")
    chat_mode = models.CharField(max_length=255, default="assistant")
    start_time = models.DateTimeField(auto_now_add=True)
    model = models.CharField(max_length=255, choices=AVAILABLE_TEXT_MODELS_CHOICES, default=AVAILABLE_TEXT_MODELS_CHOICES[0][0])
    messages = models.JSONField(default=list, null=True, blank=True)


    class Meta:
        verbose_name = "Dialog"
        verbose_name_plural = "Dialogs"
