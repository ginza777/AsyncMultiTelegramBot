from django.contrib import admin
from .models import TelegramBot, TelegramProfile

admin.site.register(TelegramBot)
admin.site.register(TelegramProfile)
