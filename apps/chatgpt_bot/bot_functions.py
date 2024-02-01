from asgiref.sync import sync_to_async
from telegram.constants import ParseMode
from telegram.ext import CallbackContext
from telegram import Update
from django.utils.translation import gettext_lazy as _

from apps.chatgpt_bot.buttons.inline_keyboard import get_chat_modes_keyboard, main_setting_keyboard, \
    ai_model_setting_keyboard, language_list_keyboard
from apps.chatgpt_bot.function.functions import HELP_MESSAGE, START_MESSAGE, IMPORTANT_MESSAGE
from apps.chatgpt_bot.function.user_get_or_create import chat_gpt_user
from utils.decarators import get_member
from apps.chatgpt_bot.models import Chat_mode


@get_member
@chat_gpt_user
async def start(update: Update, context: CallbackContext, chat_gpt_user, *args, **kwargs):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=START_MESSAGE, parse_mode="HTML")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=HELP_MESSAGE + IMPORTANT_MESSAGE,
                                   parse_mode="HTML")


@get_member
@chat_gpt_user
async def help(update: Update, context: CallbackContext, chat_gpt_user, *args, **kwargs):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=HELP_MESSAGE + IMPORTANT_MESSAGE,
                                   parse_mode="HTML")


@get_member
@chat_gpt_user
async def show_chat_modes(update: Update, context: CallbackContext, chat_gpt_user, *args, **kwargs):
    count_mode = await sync_to_async(Chat_mode.objects.count)()
    chat_modes_text = f"Select chat mode ({count_mode} modes available):"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=chat_modes_text,
                                   reply_markup=await get_chat_modes_keyboard())


@get_member
@chat_gpt_user
async def show_chat_modes_callback_handle(update: Update, context: CallbackContext, chat_gpt_user, *args, **kwargs):
    print("show_chat_modes_callback_handle")
    query = update.callback_query
    print(query.data)

    # Extracting page index from the callback data
    page_index = int(query.data.split('_')[-1])

    # Get the InlineKeyboardMarkup with pagination
    keyboard = await get_chat_modes_keyboard(page_index=page_index)

    await query.edit_message_text(
        text=f"Select a chat mode :",
        reply_markup=keyboard
    )


@get_member
@chat_gpt_user
async def set_chat_modes_callback_handle(update: Update, context: CallbackContext, chat_gpt_user, *args, **kwargs):
    query = update.callback_query
    id = query.data.split("set_chat_modes_")[-1]
    chat_mode = await sync_to_async(Chat_mode.objects.get)(id=id)
    chat_gpt_user.chat_mode = chat_mode
    await chat_gpt_user.asave()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"{chat_mode.welcome_message}", parse_mode=ParseMode.HTML
    )


@get_member
@chat_gpt_user
async def settings_handle(update: Update, context: CallbackContext, chat_gpt_user, *args, **kwargs):
    keyboard = main_setting_keyboard()
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="⚙️ Settings:",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )


@get_member
@chat_gpt_user
async def settings_choice_handle(update: Update, context: CallbackContext, chat_gpt_user, *args, **kwargs):
    callback_data_list = [{"name": "🧠 AI Model", "id": 1}, {"name": "🇺🇸 Language", "id": 2},
                          {"name": "👮‍ Your name", "id": 3}]
    query = update.callback_query
    id = query.data.split("main_setting_")[-1]
    if id == "0":
        try:
            await query.delete_message()
        except:
            pass
    if id == "1":
        keyboard = ai_model_setting_keyboard()
        await query.edit_message_text(
            text=f"Select a AI model :",
            reply_markup=keyboard
        )
    elif id == "2":
        keyboard = language_list_keyboard()
        await query.edit_message_text(
            text=f"Select a Language :",
            reply_markup=keyboard
        )
    elif id == "3":
        msg = "Send me your name. I will address you by this name! 😊"
        await query.edit_message_text(
            text=msg
        )
    else:
        pass
