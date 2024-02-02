import os

from django.conf import settings
from telegram import Bot
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, PicklePersistence

from apps.common.views import start


async def setup(token):
    print("common setup process...")
    persistence_file = os.path.join(settings.BASE_DIR, "media", "state_record", "conversationbot.pickle")
    persistence = PicklePersistence(filepath=persistence_file)
    bot = Bot(token=token)
    await bot.initialize()

    application = Application.builder().token(token).persistence(persistence).build()

    states = {}
    entry_points = [CommandHandler("start", start)]
    fallbacks = [MessageHandler(filters=None, callback=start)]

    conversation_handler = ConversationHandler(
        entry_points=entry_points,
        states=states,
        fallbacks=fallbacks,
        persistent=True,
        name="conversationbot",
    )
    application.add_handler(conversation_handler)
    await application.initialize()
    return application, bot
