import os
from django.conf import settings
from telegram import Bot, BotCommand
from telegram.ext import Application, PicklePersistence, CommandHandler, ApplicationBuilder
from apps.chatgpt_bot.bot_functions import start, help,show_chat_modes


async def post_init(application: Application):
    print("post_init function is called.")
    await application.bot.set_my_commands([
        BotCommand("/start", "Start bot"),
        BotCommand("/new", "Start new dialog"),
        BotCommand("/mode", "Select chat mode"),
        BotCommand("/retry", "Re-generate response for previous query"),
        BotCommand("/balance", "Show balance"),
        BotCommand("/settings", "Show settings"),
        BotCommand("/help", "Show help message"),
    ])


async def setup(token):
    print("chatgpt setup process...")
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
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("mode", show_chat_modes))
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handle))

    # application.add_handler(CommandHandler("help_group_chat", help_group_chat_handle))
    #
    #
    # application.add_handler(CommandHandler("retry", retry_handle))
    # application.add_handler(CommandHandler("new", new_dialog_handle))
    # application.add_handler(CommandHandler("cancel", cancel_handle))
    #
    # application.add_handler(MessageHandler(filters.VOICE , voice_message_handle))
    #

    # application.add_handler(CallbackQueryHandler(show_chat_modes_callback_handle, pattern="^show_chat_modes"))
    # application.add_handler(CallbackQueryHandler(set_chat_mode_handle, pattern="^set_chat_mode"))
    #
    # application.add_handler(CommandHandler("settings", settings_handle))
    # application.add_handler(CallbackQueryHandler(set_settings_handle, pattern="^set_settings"))
    #
    # application.add_handler(CommandHandler("balance", show_balance_handle))
    await application.initialize()
    return application, bot