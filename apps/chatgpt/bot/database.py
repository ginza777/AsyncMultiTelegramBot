# database.py
from datetime import datetime
from asgiref.sync import sync_to_async

from apps.bot.models import TelegramBot
from apps.chatgpt.functions import *
from channels.db import database_sync_to_async

from apps.chatgpt.models import ChatGptUser, Dialog, Messages_dialog
from django.utils import timezone
from typing import Optional, Any


class Database:
    def check_if_user_exists(self, user_id: int, raise_exception: bool = False):
        return ChatGptUser.objects.filter(user__telegram_id=user_id).exists()

    def add_new_user(self, user_id: int, chat_id: int):
        user = ChatGptUser.objects.create(
            user__telegram_id=user_id,
            chat_id=chat_id,
            last_interaction=timezone.now(),
            first_seen=timezone.now(),
            current_chat_mode="assistant",
            current_model="available_text_models"[0],
            n_used_tokens={},
            n_generated_images=0,
            n_transcribed_seconds=0.0
        )
        user.save()

    @database_sync_to_async
    def start_new_dialog(self, user_id: int,bot):
        bot=TelegramBot.objects.get(bot_username=bot)
        user=ChatGptUser.objects.get(user__telegram_id=user_id,user__bot=bot)
        if Dialog.objects.filter(user=user,bot=bot).exists():
            print("if dialog start_new_dialog")
            dialog_id = Dialog.objects.get(user=user,bot=bot).id
        else:
            print("else dialog start_new_dialog")
            dialog = Dialog.objects.create(
                user=user,
                chat_mode=user.current_chat_mode,
                start_time=timezone.now(),
                model=user.current_model,
                bot=bot
            )
            dialog.save()
            print(dialog.id)
            user.save()
            dialog_id = dialog.id

        return dialog_id

    def get_user_attribute(self, user_id: int, key: str):
        user = ChatGptUser.objects.get(user__telegram_id=user_id)
        return getattr(user, key, None)

    def set_user_attribute(self, user_id: int, key: str):
        user = ChatGptUser.objects.get(user__telegram_id=user_id)
        user.last_interaction = datetime.now()
        user.save()

    def update_n_used_tokens(self, user_id: int, model: str, n_input_tokens: int, n_output_tokens: int):
        user = ChatGptUser.objects.get(user__telegram_id=user_id)

        n_used_tokens_dict = user.n_used_tokens
        if model in n_used_tokens_dict:
            n_used_tokens_dict[model]["n_input_tokens"] += n_input_tokens
            n_used_tokens_dict[model]["n_output_tokens"] += n_output_tokens
        else:
            n_used_tokens_dict[model] = {
                "n_input_tokens": n_input_tokens,
                "n_output_tokens": n_output_tokens
            }

        user.n_used_tokens = n_used_tokens_dict
        user.save()

    @sync_to_async()
    def get_dialog_messages(self, user_id,bot,msg:None):
        bot=TelegramBot.objects.get(bot_username=bot)
        user=ChatGptUser.objects.get(user__telegram_id=user_id,user__bot=bot)
        if Dialog.objects.filter(user=user,bot=bot).exists():
            print("if dialog get_dialog_messages")
            dialog = Dialog.objects.get(user=user,bot=bot)
        else:

            print("else dialog get_dialog_messages")
            dialog = Dialog.objects.create(
                user=user,
                chat_mode=user.current_chat_mode,
                start_time=timezone.now(),
                model=user.current_model,
                bot=bot,
            )

            dialog.save()

        msg_dialog=Messages_dialog.objects.create(
            user=msg,
            assisant="",
            dialog=dialog
        ).save()
        dialog_id = dialog.id
        print(user_id, dialog_id)

        messages = Messages_dialog.objects.filter(dalog=dialog)

        formatted_messages = [
            {"user": msg.user, "assistant": msg.assisant}
            for msg in messages
        ]

        return formatted_messages





    @sync_to_async()
    def set_dialog_messages(seld,user_id, new_dialog_messages,bot):
        bot=TelegramBot.objects.get(bot_username=bot)
        user=ChatGptUser.objects.get(user__telegram_id=user_id,user__bot=bot)
        if Dialog.objects.filter(user=user,bot=bot).exists():
            print("if dialog set_dialog_messages")
            dialog_id = Dialog.objects.get(user=user,bot=bot).id
        else:
            print("else dialog set_dialog_messages")
            dialog = Dialog.objects.create(
                user=user,
                chat_mode=user.current_chat_mode,
                start_time=timezone.now(),
                model=user.current_model,
                bot=bot
            )
            dialog.save()
            print(dialog.id)
            user.save()
            dialog_id = dialog.id

        dialog=Dialog.objects.get(id=dialog_id)
        dialog.messages = dialog.messages + new_dialog_messages
        dialog.save()
