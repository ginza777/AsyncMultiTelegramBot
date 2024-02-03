from django.utils import timezone
from django.utils.translation import activate

from apps.bot_main_setup.models import TelegramProfile
from apps.chatgpt_bot.models import ChatGptUser


def chat_gpt_user(func):
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
        print(f"User: {user}")
        try:
            chat_gpt_user = await ChatGptUser.objects.aget(user=user)
        except ChatGptUser.DoesNotExist:
            chat_gpt_user = await ChatGptUser.objects.acreate(
                user=user,
                chat_id=user.telegram_id,
            )
        chat_gpt_user.last_interaction = timezone.now()
        await chat_gpt_user.asave()
        activate("en")
        return await func(update, context, chat_gpt_user, *args, **kwargs)

    return wrap
