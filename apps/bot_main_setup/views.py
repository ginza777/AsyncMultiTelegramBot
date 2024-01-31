import json
from asgiref.sync import sync_to_async
from django.http import JsonResponse
from telegram import Update
from apps.bot_main_setup.models import TelegramBot
from apps.chatgpt_bot.views import setup as setup_chatgpt
from apps.common.bot import setup as setup_common


@sync_to_async
def check_bot_token(bot_token):
    return TelegramBot.objects.filter(bot_token=bot_token).exists()


@sync_to_async
def get_bot_app_name(bot_token):
    return TelegramBot.objects.get(bot_token=bot_token).app_name


async def token_checker(bot_token):
    if await check_bot_token(bot_token):
        print("Bot found...")
        return JsonResponse({"status": "ok"})
    else:
        print("Bot not found...")
        return JsonResponse({"error": "Bot not found"}, status=404)


async def setup_choice(bot_token):
    app_name = await get_bot_app_name(bot_token)
    if app_name == "setup_chatgpt":
        print("choiced setup_chatgpt")
        return setup_chatgpt
    elif app_name == "setup_common":
        print("choiced setup_common")
        return setup_common


async def handle_telegram_webhook(request, bot_token):
    print("handle_telegram_webhook...")
    print("bot_token: ", bot_token)
    await token_checker(bot_token)
    setup = await setup_choice(bot_token)
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
