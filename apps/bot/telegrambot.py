import datetime
import logging

import telegram
from django.conf import settings
from django.core.exceptions import BadRequest
from django.utils import timezone
from telegram import Update
from telegram.ext import CallbackContext
from django.utils.translation import gettext_lazy as _, activate

from apps.bot import models
from utils.decarators import get_member

logger = logging.getLogger(__name__)


@get_member
async def start(update: Update, context: CallbackContext, tg_user: models.TelegramProfile):
    """Send a message asynchronously when the command /start is issued."""

    try:
        await update.message.reply_text("Assalomu alaykum, bot ishladi")
    except Exception as e:
        logger.error(f"Error in start command: {e}")
