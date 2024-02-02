from asgiref.sync import sync_to_async
from telegram.constants import ParseMode
from telegram.ext import CallbackContext
from telegram import Update
from apps.chatgpt_bot.buttons.inline_keyboard import get_chat_modes_keyboard, main_setting_keyboard, \
    ai_model_setting_keyboard, language_list_keyboard, back_settings
from apps.chatgpt_bot.buttons.keyboard import generate_keyboard
from apps.chatgpt_bot.function.functions import HELP_MESSAGE, START_MESSAGE, IMPORTANT_MESSAGE, \
    get_current_model, get_user_token, get_current_chat_mode, save_custom_language, new_diaolog, new_diaolog_sync
from apps.chatgpt_bot.function.user_get_or_create import chat_gpt_user
from apps.chatgpt_bot.openai_integrations.token_calculator import num_tokens_from_messages
from utils.decarators import get_member
from apps.chatgpt_bot.models import Chat_mode, ChatGptUser, GptModels
from apps.chatgpt_bot.openai_integrations.openai import send_message_stream


@get_member
@chat_gpt_user
async def start(update: Update, context: CallbackContext, chat_gpt_user, *args, **kwargs):
    buttons = ["My_account", "New_dialog", "Retry", "Chat_mode", "Settings", "Help", "About_us", "Contact_us"]
    my_list = buttons
    reply_markup = generate_keyboard(my_list)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=START_MESSAGE, parse_mode="HTML")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=HELP_MESSAGE + IMPORTANT_MESSAGE,
                                   parse_mode="HTML", reply_markup=reply_markup)


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


@sync_to_async
def set_chat_modes(chat_gpt_user, id):
    new_diaolog_sync(chat_gpt_user)
    chat_mode = Chat_mode.objects.get(id=id)
    chat_gpt_user.current_chat_mode = chat_mode
    if chat_gpt_user.current_model is None or chat_gpt_user.current_model == "null":
        chat_gpt_user.current_model = GptModels.objects.get(model="gpt-3.5-turbo-0125")
    chat_gpt_user.save()


@get_member
@chat_gpt_user
async def set_chat_modes_callback_handle(update: Update, context: CallbackContext, chat_gpt_user: ChatGptUser, *args,
                                         **kwargs):
    query = update.callback_query
    print(100 * "*")
    chat_mode = await sync_to_async(Chat_mode.objects.get)(id=query.data.split("set_chat_modes_")[-1])
    await set_chat_modes(chat_gpt_user, query.data.split("set_chat_modes_")[-1])
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"{chat_mode.welcome_message}", parse_mode=ParseMode.HTML
    )


@get_member
@chat_gpt_user
async def settings_handle(update: Update, context: CallbackContext, chat_gpt_user, *args, **kwargs):
    print("settings_handle")
    print(update)
    if update.message and update.message.entities and update.message.entities[0].type == "bot_command":
        if update.message.text == "/settings":
            keyboard = main_setting_keyboard()
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text="⚙️ Settings:",
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )

    if update.callback_query and update.callback_query.data == "setting_back":
        print("callback_query")
        print(update.callback_query.data)
        keyboard = main_setting_keyboard()
        await update.callback_query.edit_message_text(
            text="⚙️ Settings:",
            reply_markup=keyboard,
        )

    if update.callback_query and update.callback_query.data == "delete_setting_back":
        print("callback_query")
        print(update.callback_query.data)
        keyboard = main_setting_keyboard()
        await update.callback_query.delete_message()


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


@get_member
@chat_gpt_user
async def message_handle(update: Update, context: CallbackContext, chat_gpt_user: ChatGptUser, *args, **kwargs):
    text = update.message.text
    model_name = await get_current_model(chat_gpt_user)
    chat_token = await get_user_token(chat_gpt_user)

    await send_message_stream(text, model_name, chat_token, chat_gpt_user, update, context)


@get_member
@chat_gpt_user
async def language_choice_handle(update: Update, context: CallbackContext, chat_gpt_user: ChatGptUser, *args, **kwargs):
    Language = {
        "uz": "Uzbek",
        "en": "English",
        "ru": "Russian",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
    }

    query = update.callback_query
    id = query.data.split("language_setting_")[-1]
    print("custom lang: ", id)
    await save_custom_language(chat_gpt_user, id)
    await query.edit_message_text(
        text=f"You choice language is {Language[id]} ",
        reply_markup=back_settings()
    )


@get_member
@chat_gpt_user
async def new_dialog_handle(update: Update, context: CallbackContext, chat_gpt_user: ChatGptUser, *args, **kwargs):
    status = await new_diaolog(chat_gpt_user)
    if status:
        message = "You created new dialogue!"
    else:
        message = "You have not dialogue yet!"

    await update.message.reply_text(message)
