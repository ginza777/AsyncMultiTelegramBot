from apps.bot_main_setup.models import TelegramProfile
from apps.translator_bot.models import TranslatorUser


def translator_user(func):
    async def wrap(update, context, *args, **kwargs):
        print(100 * "=")
        user_id, first_name, last_name, username = 0, "", "", ""

        print(100 * "*")
        try:
            if update.message.chat.type == "private":
                print("Private Chat")
                user_id = update.message.chat_id
                first_name = update.effective_user.first_name
                last_name = update.effective_user.last_name
                username = update.effective_user.username
            elif update.message.chat.type == "group" or update.message.chat.type == "supergroup":
                print("Group Chat,type=", update.message.chat.type)
                user_id = update.message.from_user.id
                first_name = update.message.from_user.first_name
                last_name = update.message.from_user.last_name
                username = update.message.from_user.username
            elif update.callback_query:
                user_id = update.callback_query.from_user.id
                first_name = update.callback_query.from_user.first_name
                last_name = update.callback_query.from_user.last_name
                username = update.callback_query.from_user.username
        except AttributeError:
            user_id = update.callback_query.from_user.id
            first_name = update.callback_query.from_user.first_name
            last_name = update.callback_query.from_user.last_name
            username = update.callback_query.from_user.username

        print("User ID:", user_id)
        print("First Name:", first_name)
        print("Last Name:", last_name)
        print("Username:", username)

        user = await TelegramProfile.objects.aget(telegram_id=user_id)
        lang= user.language
        print(f"User: {user}")
        try:
            translator_user = await TranslatorUser.objects.aget(user=user)
        except TranslatorUser.DoesNotExist:
            translator_user = await TranslatorUser.objects.acreate(
                user=user,
            )
        await translator_user.asave()
        return await func(update, context, translator_user, *args, **kwargs)

    return wrap
