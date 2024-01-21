from django.conf import settings
from telegram.ext import Application
import requests


async def set_webhook(bot_token):
    webhook_url = settings.WEBHOOK_URL

    application = Application.builder().token(bot_token).build()

    await application.bot.set_webhook(f"{webhook_url}/bot/handle_telegram_webhook/{bot_token}")
    print("Webhook set successfully for bot: {}".format((await application.bot.get_me()).username))


def get_info(bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    response = requests.post(url)
    return response.json().get("result").get("username"), response.json().get("result").get("first_name")
