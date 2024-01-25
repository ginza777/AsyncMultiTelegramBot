import datetime
from utils.decarators import get_member
import logging
from telegram.ext import  CallbackContext
from telegram import  Update
from .functions import  *
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)




@get_member
async def start(update: Update, context: CallbackContext, tg_user: TelegramProfile):
    try:
        user_exists = await check_user_exists(tg_user)

        if user_exists:
            user = await get_user(tg_user)
        else:
            user = await create_user(tg_user)

        user.last_interaction = datetime.datetime.now()
        user.current_dialog_id = str(uuid.uuid4()) # Assuming start_new_dialog is an asynchronous function
        await database_sync_to_async(user.save)()  # Save the user asynchronously

        start_message = START_MESSAGE
        help_message = HELP_MESSAGE
        important_message = IMPORTANT_MESSAGE
        await update.message.reply_text(start_message +'\n\n'+ help_message+'\n\n'+important_message, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error in start command: {e}")



