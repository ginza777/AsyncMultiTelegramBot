from django.contrib import admin

from .models import TelegramBot, TelegramProfile, BackupSenderBot


@admin.register(TelegramBot)
class TelegramBotAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "bot_token", "bot_username", "app_name")


@admin.register(TelegramProfile)
class TelegramProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "username", "telegram_id", "language")
    filter_horizontal = ("bot",)


@admin.register(BackupSenderBot)
class BackupSenderBotAdmin(admin.ModelAdmin):
    list_display = ("id", "token", "channel_id")