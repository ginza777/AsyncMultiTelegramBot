# Create your views here.
import logging
from googletrans import Translator
from telegram import Update
from telegram.ext import CallbackContext

from apps.bot_main_setup.models import TelegramProfile
from utils.decarators import get_member

logger = logging.getLogger(__name__)


@get_member
async def start(update: Update, context: CallbackContext,*args, **kwargs):
    print("start",update.effective_user.username )
    """Send a message asynchronously when the command /start is issued."""
    message = "if you have some questions or questions about bot creation you can contact the creator via the link below => "+'<a href="https://t.me/+998939708050">ADMIN</a>'
    try:
        await update.message.reply_html(message)
    except Exception as e:
        logger.error(f"Error in start command: {e}")



@get_member
async def translator(update: Update, context: CallbackContext,*args, **kwargs):
    msg=update.message.text
    await translator.translate(msg)
    await update.message.reply_text(translator.translate(msg))