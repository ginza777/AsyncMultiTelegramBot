from functools import wraps
from asgiref.sync import sync_to_async
from django.utils.translation import activate

from apps.bot_main_setup.models import TelegramProfile
from apps.chatgpt_bot.models import ChatGptUser
from django.utils import timezone

def chat_gpt_user(func):
    async def wrap(update, context, *args, **kwargs):
        user = await TelegramProfile.objects.aget(telegram_id=update.effective_user.id)
        try:
            chat_gpt_user = await ChatGptUser.objects.aget(user=user)
        except ChatGptUser.DoesNotExist:
            chat_gpt_user = await ChatGptUser.objects.acreate(user=user, chat_id=update.effective_chat.id)
        chat_gpt_user.last_interaction = timezone.now()
        await chat_gpt_user.asave()
        activate('en')
        return await func(update, context, chat_gpt_user, *args, **kwargs)

    return wrap
