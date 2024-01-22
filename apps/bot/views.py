import os
import json
from django.http import JsonResponse
from django.conf import settings
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ConversationHandler, PicklePersistence, filters, MessageHandler
from .telegrambot import start

async def setup(token):
    persistence_file = os.path.join(settings.BASE_DIR, "media", "state_record", "conversationbot.pickle")
    persistence = PicklePersistence(filepath=persistence_file)
    bot = Bot(token=token)
    await bot.initialize()

    application = Application.builder().token(token).persistence(persistence).build()

    states = {

    }
    entry_points = [CommandHandler('start', start)]
    fallbacks = [CommandHandler('start', start)]

    conversation_handler = ConversationHandler(
        entry_points=entry_points,
        states=states,
        fallbacks=fallbacks,
        persistent=True,
        name="conversationbot",
    )
    application.add_handler(conversation_handler)
    # application.add_handler(CommandHandler(
    #     'chat', prompt, filters=filters.ChatType.GROUP | filters.ChatType.SUPERGROUP)
    # )
    # application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND),prompt))
    await application.initialize()
    return application, bot


async def handle_telegram_webhook(request, bot_token):
    try:
        application, bot = await setup(bot_token)
        body = request.body
        data = json.loads(body.decode('utf-8'))
        update = Update.de_json(data, bot)

        if update.message and update.message.chat.type == 'private':
            await application.process_update(update)

        return JsonResponse({"status": "ok"})
    except json.JSONDecodeError as e:
        print(e)
        return JsonResponse({"error": "Invalid JSON"}, status=400)
