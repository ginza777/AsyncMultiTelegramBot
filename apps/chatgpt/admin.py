from django.contrib import admin
from .models import ChatGptUser, Dialog, Chat_mode, Config, GptModels, Messages_dialog


@admin.register(Messages_dialog)
class MessagesAdmin(admin.ModelAdmin):
    list_display = ("user",)


@admin.register(ChatGptUser)
class TelegramProfileAdmin(admin.ModelAdmin):
    list_display = ("id","chat_id","current_chat_mode","current_model","last_interaction")


@admin.register(Dialog)
class DialogAdmin(admin.ModelAdmin):
    list_display = ("id","user","chat_mode","model",)

@admin.register(Chat_mode)
class ChatModeAdmin(admin.ModelAdmin):
    list_display = ("id","model_name",)

admin.site.register(Config)
@admin.register(GptModels)
class GptModelsAdmin(admin.ModelAdmin):
    list_display = ("model",)
