from utils.decarators import get_member
from .models import TelegramProfile
import logging
from telegram.ext import  CallbackContext
from telegram import Message, MessageEntity, Update
from openai import AsyncOpenAI

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


@get_member
async def chat(update: Update, context: CallbackContext, tg_user: TelegramProfile):
    user_id = update.effective_user.id
    api_key = "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"

    session_manager = ChatGPTSessionManager()
    chat_gpt_client = session_manager.get_chat_gpt_client(user_id, api_key)

    try:
        user_input = update.message.text
        response = await chat_gpt_client.get_assistant_response(user_input)
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Error in chat command: {e}")

class ChatGPTSessionManager:
    def __init__(self):
        self.clients = {}

    def get_chat_gpt_client(self, user_id, api_key):
        if user_id not in self.clients:
            self.clients[user_id] = ChatGPTClient(api_key=api_key)
        return self.clients[user_id]

# ChatGPTClient
class ChatGPTClient:
    def __init__(self, api_key):
        self.client = AsyncOpenAI(api_key=api_key)
        self.user_contexts = []

    async def get_user_context(self):
        return self.user_contexts

    async def update_user_context(self, message):
        self.user_contexts.append({"role": "user", "content": message})

    async def get_assistant_response(self, message):
        await self.update_user_context(message)
        user_context = await self.get_user_context()

        completion = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=user_context
        )
        response = completion.choices[0].message.content
        await self.update_user_context(response)
        return response
