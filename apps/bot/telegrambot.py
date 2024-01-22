import datetime
import logging
from dotenv import load_dotenv
import telegram
from django.conf import settings
from django.core.exceptions import BadRequest
from django.utils import timezone
from telegram import Update
from telegram.ext import CallbackContext, ContextTypes
from django.utils.translation import gettext_lazy as _, activate
from utils.decarators import get_member
from .models import TelegramProfile

#######
# from __future__ import annotations

import asyncio
import logging
import os
import io

from uuid import uuid4
from telegram import BotCommandScopeAllGroupChats, Update, constants
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle
from telegram import InputTextMessageContent, BotCommand
from telegram.error import RetryAfter, TimedOut, BadRequest
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, \
    filters, InlineQueryHandler, CallbackQueryHandler, Application, ContextTypes, CallbackContext

from pydub import AudioSegment
from PIL import Image

from telegram import Message, MessageEntity, Update, ChatMember, constants


logger = logging.getLogger(__name__)

def message_text(message: Message) -> str:
    """
    Returns the text of a message, excluding any bot commands.
    """
    message_txt = message.text
    if message_txt is None:
        return ''

    for _, text in sorted(message.parse_entities([MessageEntity.BOT_COMMAND]).items(),
                          key=(lambda item: item[0].offset)):
        message_txt = message_txt.replace(text, '').strip()

    return message_txt if len(message_txt) > 0 else ''


@get_member
async def start(update: Update, context: CallbackContext, tg_user: TelegramProfile):
    """Send a message asynchronously when the command /start is issued."""


    try:
        await update.message.reply_text("Assalomu alaykum, bot ishladi")
    except Exception as e:
        logger.error(f"Error in start command: {e}")

