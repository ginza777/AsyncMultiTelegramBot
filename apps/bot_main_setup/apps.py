import asyncio
import requests.exceptions
from asgiref.sync import sync_to_async
from django.apps import AppConfig
import telegram
import django.core.exceptions
from django.core.management import call_command

from utils.bot import set_webhook
import environ
from django.db.utils import ProgrammingError
from apps.bot_main_setup.function.createsuperuser import create_superuser

env = environ.Env()
environ.Env.read_env()
import traceback


class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.bot_main_setup'

    def ready(self):
        # call_command('migrate', interactive=False)
        asyncio.run(create_superuser())
        asyncio.run(self.setup_webhook())

    async def setup_webhook(self):
        print("setup_webhook...")
        try:
            bot_tokens = await self.get_bot_tokens()
            print("bot_tokens: ", bot_tokens)
            for bot_token in bot_tokens:
                await set_webhook(bot_token)
        except telegram.error.RetryAfter:
            pass
        except requests.exceptions.ConnectionError:
            print("Connection error. Please check your internet connection.")
        except django.core.exceptions.ImproperlyConfigured:
            print("Improperly configured. Please check your settings.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            traceback.print_exc()

    @sync_to_async
    def get_bot_tokens(self):
        try:
            from apps.bot_main_setup.models import TelegramBot
            bot_tokens = list(TelegramBot.objects.all().values_list("bot_token", flat=True))
        except ProgrammingError:
            bot_tokens = []
        return bot_tokens
