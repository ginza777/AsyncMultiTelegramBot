import asyncio
import requests.exceptions
from django.apps import AppConfig
from django.conf import settings
import telegram
import django.core.exceptions
from utils.bot import set_webhook


class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.bot'

    def ready(self):
        asyncio.run(self.setup_webhook())

    async def setup_webhook(self):
        try:
            bot_token = settings.BOT_TOKEN
            await set_webhook(bot_token)
        except telegram.error.RetryAfter:
            pass
        except requests.exceptions.ConnectionError:
            print("Connection error. Please check your internet connection.")
        except django.core.exceptions.ImproperlyConfigured:
            print("Improperly configured. Please check your settings.")
        except telegram.error.Unauthorized:
            print("Unauthorized. Please check your bot token.")

