from channels.db import database_sync_to_async
from django.utils.translation import activate
from apps.bot_main_setup import models


def get_member(func):
    async def wrap(update, context, *args, **kwargs):
        try:
            user_id = update.message.chat_id
        except AttributeError:
            user_id = update.callback_query.message.chat_id
        bot = await models.TelegramBot.objects.aget(bot_username=context.bot.username)


        language_code = update.effective_user.language_code
        try:
            selected_language = models.Language(language_code)
        except ValueError:
            # Handle the case where the language code is not in Language choices
            selected_language = models.Language.UZBEK  # Set a default language or handle accordingly
            print(f"Language code '{language_code}' not found in choices. Using default language.")

        print(f"Selected Language: {selected_language}")
        user, created = await models.TelegramProfile.objects.aget_or_create(
            telegram_id=user_id,
            defaults={
                'first_name': update.effective_user.first_name,
                'last_name': update.effective_user.last_name,
                'username': update.effective_user.username,
                'language':selected_language,

            }
        )

        if not created:

            user.first_name = update.effective_user.first_name
            user.last_name = update.effective_user.last_name
            user.username = update.effective_user.username
            user.language = selected_language
            await database_sync_to_async(user.bot.add)(bot)
            await user.asave()
        else:
            user.language = selected_language
            await database_sync_to_async(user.bot.add)(bot)
            await database_sync_to_async(user.asave)()
        activate('en')
        return await func(update, context, user, *args, **kwargs)

    return wrap
