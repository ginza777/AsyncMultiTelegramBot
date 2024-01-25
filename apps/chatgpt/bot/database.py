# database.py
from datetime import datetime

from channels.db import database_sync_to_async

from apps.chatgpt.models import ChatGptUser, Dialog
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
            current_dialog_id=None,
            current_chat_mode="assistant",
            current_model="available_text_models"[0],
            n_used_tokens={},
            n_generated_images=0,
            n_transcribed_seconds=0.0
        )
        user.save()

    @database_sync_to_async
    def start_new_dialog(self, user_id: int):
        user = ChatGptUser.objects.get(user__telegram_id=user_id)

        dialog = Dialog.objects.create(
            user=user,
            chat_mode=user.current_chat_mode,
            start_time=timezone.now(),
            model=user.current_model,
            messages=[]
        )
        dialog.save()

        user.current_dialog_id = dialog.id
        user.save()

        return dialog.id

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

    def get_dialog_messages(self, user_id: int, dialog_id: Optional[str] = None):
        if dialog_id is None:
            dialog_id = self.get_user_attribute(user_id, "current_dialog_id")

        dialog = Dialog.objects.get(id=dialog_id, user__user__telegram_id=user_id)
        return dialog.messages

    def set_dialog_messages(self, user_id: int, dialog_messages: list, dialog_id: Optional[str] = None):
        if dialog_id is None:
            dialog_id = self.get_user_attribute(user_id, "current_dialog_id")

        dialog = Dialog.objects.get(id=dialog_id, user__user__telegram_id=user_id)
        dialog.messages = dialog_messages
        dialog.save()
