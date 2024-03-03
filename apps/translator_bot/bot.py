import os

from django.conf import settings
from telegram import Bot, BotCommand
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    PicklePersistence,
    filters,
)

from apps.chatgpt_bot.bot_functions import (
    start,
)
from apps.common.views import start as about
from apps.translator_bot.views import start, translator, set_target_lang, set_native_lang, settings_user


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
    application.add_handler(CallbackQueryHandler(start, pattern="^setting_back_to_native_lang"))
    application.add_handler(CallbackQueryHandler(set_target_lang, pattern="^language_target_"))
    application.add_handler(CallbackQueryHandler(set_native_lang, pattern="^language_native_"))

    application.add_handler(CommandHandler("settings", settings_user))
    application.add_handler(CallbackQueryHandler(settings_user, pattern="^language_reset_native_"))
    application.add_handler(CallbackQueryHandler(settings_user, pattern="^language_reset_target_"))
    application.add_handler(CallbackQueryHandler(settings_user, pattern="^change_lang_native"))
    application.add_handler(CallbackQueryHandler(settings_user, pattern="^change_lang_target"))
    application.add_handler(MessageHandler(filters.Regex(r"^Change Language$"), settings_user))
    application.add_handler(MessageHandler(filters.Regex(r"^About$"), about))
    application.add_handler(MessageHandler(filters.Regex(r"^Restart$"), start))
    application.add_handler(MessageHandler(filters.Regex(r"^History conversation$"), start))

    application.add_handler(MessageHandler(filters.ALL, translator))

    # # callback
    # application.add_handler(CallbackQueryHandler(show_chat_modes_callback_handle, pattern="^show_chat_modes"))

    await application.initialize()
    return application, bot
