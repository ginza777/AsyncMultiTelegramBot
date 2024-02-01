from asgiref.sync import sync_to_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from apps.chatgpt_bot.models import Chat_mode


async def get_chat_modes_keyboard():
    chat_modes = await sync_to_async(Chat_mode.objects.all)()
    keyboard = []
    async for chat_mode in chat_modes:
        await keyboard.append([InlineKeyboardButton(chat_mode.model_name, callback_data=f"set_chat_mode_{chat_mode.id}")])
    return InlineKeyboardMarkup(keyboard)