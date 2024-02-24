import time

import environ
import requests
from django.core.management.base import BaseCommand

from apps.bot_main_setup.models import TelegramBot

env = environ.Env()
env.read_env(".env")

bot_webhook_url = env.str("WEBHOOK_URL")


def set_webhook_sync(bot_token):
    webhook_url = bot_webhook_url
    url = (
        f"https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook_url}/bot/handle_telegram_webhook/{bot_token}"
    )
    response = requests.post(url)
    print(response.json())
    return response.json()


# Corrected class name to "Commands"
class Command(BaseCommand):
    help = "Check webhook info"

    def handle(self, *args, **options):
        bots = TelegramBot.objects.all()
        for bot in bots:
            set_webhook_sync(bot.bot_token)
            time.sleep(5)
