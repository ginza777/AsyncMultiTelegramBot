from apps.translator_bot.models import TranslatorUser, TranslatorConversation
from django.contrib import admin


@admin.register(TranslatorUser)
class TranslatorUserAdmin(admin.ModelAdmin):
    list_display = ("user", "native_language", "target_language")


@admin.register(TranslatorConversation)
class TranslatorAdmin(admin.ModelAdmin):
    list_display = ("user", "text", "translated_text", "source_language", "target_language", "created_at")
    list_filter = ("source_language", "target_language", "created_at")
