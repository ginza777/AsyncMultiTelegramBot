from asgiref.sync import sync_to_async
from telegram.ext import CallbackContext
from telegram import Update
from django.utils.translation import gettext_lazy as _

from apps.chatgpt_bot.buttons.inline_keyboard import get_chat_modes_keyboard
from apps.chatgpt_bot.function.functions import HELP_MESSAGE, START_MESSAGE, IMPORTANT_MESSAGE
from apps.chatgpt_bot.function.user_get_or_create import chat_gpt_user
from utils.decarators import get_member
from apps.chatgpt_bot.models import Chat_mode

@get_member
@chat_gpt_user
async def start(update:Update, context:CallbackContext, chat_gpt_user, *args, **kwargs):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=START_MESSAGE,parse_mode="HTML")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=HELP_MESSAGE+IMPORTANT_MESSAGE, parse_mode="HTML")


@chat_gpt_user
async def help(update:Update, context:CallbackContext, chat_gpt_user, *args, **kwargs):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=HELP_MESSAGE+IMPORTANT_MESSAGE, parse_mode="HTML")

@chat_gpt_user
async def show_chat_modes(update:Update, context:CallbackContext, chat_gpt_user, *args, **kwargs):
    count_mode = await sync_to_async(Chat_mode.objects.count)()
    chat_modes_text=f"Select chat mode ({count_mode} modes available):"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=chat_modes_text,reply_markup=await get_chat_modes_keyboard())