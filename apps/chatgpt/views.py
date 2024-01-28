import datetime

from telegram.constants import ParseMode


import logging
from .functions import  *
from channels.db import database_sync_to_async
import io
import logging
import asyncio
import traceback
import html
import json
from datetime import datetime
import openai

import telegram
from telegram import (
    Update,
    User,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    AIORateLimiter,
    filters
)
from telegram.constants import ParseMode, ChatAction


logger = logging.getLogger(__name__)

@get_member
async def start(update: Update, context: CallbackContext, tg_user: TelegramProfile):
    try:
        user_exists = await check_user_exists(tg_user)

        if user_exists:
            user = await get_user(tg_user)
        else:
            user = await create_user(tg_user)

        start_message = START_MESSAGE
        help_message = HELP_MESSAGE
        important_message = IMPORTANT_MESSAGE
        await update.message.reply_text(start_message +'\n\n'+ help_message+'\n\n'+important_message, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error in start command: {e}")

