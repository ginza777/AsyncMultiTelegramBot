#https://api.telegram.org/bot6583031063:AAEqXsMOj2zJbU2AY_yNlwAX3CgB6gZ0RXU/setWebhook?url=https://faf1-95-214-210-11.ngrok-free.app
from apps.bot_main_setup.models import TelegramBot
from django.core.management.base import BaseCommand
import requests
import environ

env = environ.Env()
env.read_env(".env")

bot_webhook_url = env.str("WEBHOOK_URL")


# Corrected class name to "Commands"
class Command(BaseCommand):
    help = 'Check webhook info'

    def handle(self, *args, **options):
        bots = TelegramBot.objects.all()
        for bot in bots:
            url = f"https://api.telegram.org/bot{bot.bot_token}/getWebhookInfo"
            response = requests.post(url)
            print(response.json())
