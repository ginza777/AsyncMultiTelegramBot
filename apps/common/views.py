# Create your views here.
import logging

from telegram import Update
from telegram.ext import CallbackContext

from apps.bot_main_setup.models import TelegramProfile
from utils.decarators import get_member

logger = logging.getLogger(__name__)


@get_member
async def start(update: Update, context: CallbackContext, tg_user: TelegramProfile):
    """Send a message asynchronously when the command /start is issued."""

    try:
        await update.message.reply_text("Assalomu alaykum, common bot ishladi")
    except Exception as e:
        logger.error(f"Error in start command: {e}")
