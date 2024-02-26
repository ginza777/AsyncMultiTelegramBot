import os

from django.conf import settings
from telegram import Bot, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, PicklePersistence, \
    ApplicationBuilder, filters
from apps.translator_bot.views import start,translator
from apps.common.views import start as about

async def post_init(application: Application):
    print("post_init function is called.")
    await application.bot.set_my_commands(
        [
            BotCommand("/start", "Start bot"),
            BotCommand("/new", "Start new dialog"),
            BotCommand("/mode", "Select chat mode"),
            BotCommand("/retry", "Re-generate response for previous query"),
            BotCommand("/balance", "Show balance"),
            BotCommand("/settings", "Show settings"),
            BotCommand("/help", "Show help message"),
        ]
    )


async def setup(token):
    print("caption killer setup process...")
    persistence_file = os.path.join(settings.BASE_DIR, "media", "state_record", "conversationbot.pickle")
    persistence = PicklePersistence(filepath=persistence_file)
    bot = Bot(token=token)
    await bot.initialize()
    application = (
        ApplicationBuilder()
        .token(token)
        .concurrent_updates(True)
        .http_version("1.1")
        .get_updates_http_version("1.1")
        .post_init(post_init)
        .persistence(persistence)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("about", about))
    # application.add_handler(MessageHandler(filters.ALL, translator))

    # # callback
    # application.add_handler(CallbackQueryHandler(show_chat_modes_callback_handle, pattern="^show_chat_modes"))

    await application.initialize()
    return application, bot
