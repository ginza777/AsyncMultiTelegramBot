
from telegram.ext import CallbackContext
from telegram import Update
from django.utils.translation import gettext_lazy as _
from apps.chatgpt_bot.function.functions import HELP_MESSAGE, START_MESSAGE, IMPORTANT_MESSAGE
from apps.chatgpt_bot.function.user_get_or_create import chat_gpt_user
from utils.decarators import get_member


@get_member
@chat_gpt_user
async def start(update:Update, context:CallbackContext, chat_gpt_user, *args, **kwargs):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=START_MESSAGE)


@chat_gpt_user
async def help(update:Update, context:CallbackContext, chat_gpt_user, *args, **kwargs):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=HELP_MESSAGE+IMPORTANT_MESSAGE, parse_mode="HTML")