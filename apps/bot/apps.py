import asyncio
import requests.exceptions
from asgiref.sync import sync_to_async
from django.apps import AppConfig
import telegram
import django.core.exceptions
from utils.bot import set_webhook
from django.core.management import call_command


class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.bot'

    def ready(self):

        call_command('migrate', interactive=False)
        asyncio.run(self.setup_webhook())
    async def setup_webhook(self):
        try:
            bot_tokens =await self.get_bot_tokens()
            for bot_token in bot_tokens:
                await set_webhook(bot_token)
        except telegram.error.RetryAfter:
            pass
        except requests.exceptions.ConnectionError:
            print("Connection error. Please check your internet connection.")
        except django.core.exceptions.ImproperlyConfigured:
            print("Improperly configured. Please check your settings.")

    @sync_to_async
    def get_bot_tokens(self):
        from apps.bot.models import TelegramBot
        bot_tokens =  list(TelegramBot.objects.all().values_list("bot_token", flat=True))
        return bot_tokens

