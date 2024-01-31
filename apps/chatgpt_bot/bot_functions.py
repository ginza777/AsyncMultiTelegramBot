
from telegram.ext import CallbackContext
from telegram import Update

from apps.chatgpt_bot.function.user_get_or_create import chat_gpt_user
from utils.decarators import get_member


@get_member
@chat_gpt_user
async def start(update:Update, context:CallbackContext, chat_gpt_user, *args, **kwargs):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")