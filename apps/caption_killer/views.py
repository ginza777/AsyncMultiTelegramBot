# Create your views here.
import logging

from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import CallbackContext

from apps.bot_main_setup.log_chat import send_msg_log
from apps.caption_killer.models import Keyword, Channel

logger = logging.getLogger(__name__)


async def cap_killer(update: Update, context: CallbackContext):
    """Send a message asynchronously when the command /start is issued."""
    if update.channel_post and update.channel_post.chat.type == "channel":
        print("this is channel message")
        chat_id = update.channel_post.chat.id
        message_id = update.channel_post.message_id
        caption = update.channel_post.caption or ''
        new_caption = await filter_caption(caption, chat_id)
        # print(new_caption)
        try:
            if Channel.objects.filter(channel_id=chat_id).exists():
                await context.bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=new_caption)
            else:
                message = "adminga qo'shilmagan" + f"""{update.channel_post}"""
                await send_msg_log(message)
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            message = "caption killer bot\n" + f"Error in start command: {e}"
            await send_msg_log(message)


@sync_to_async
def filter_caption(caption: str, channel_id) -> str:
    print(channel_id)
    if Channel.objects.filter(channel_id=channel_id).exists():
        print("channel exist")
        channel = Channel.objects.get(channel_id=channel_id)
        keyword_texts = Keyword.objects.filter(channel=channel)
        keyword_text_list = [keyword.text for keyword in keyword_texts]
        print("channel:", channel)
        print(keyword_text_list)
        for key_word in keyword_text_list:
            caption.replace(key_word, '')
        # caption = '\n'.join(line for line in caption.splitlines() if line.strip())
        caption += F"\n\n•┈┈┈•• ✦🍃✦••┈┈┈•\n\n{channel.channel_sign}"
        return caption
    return caption
