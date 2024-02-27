# Create your views here.
import logging

# from googletrans import Translator
from telegram import Update
from telegram.ext import CallbackContext

from apps.bot_main_setup.models import TelegramProfile
from apps.chatgpt_bot.buttons.keyboard import generate_keyboard
from apps.translator_bot.buttons.inline_keyboard import language_list, \
    language_list_keyboard, inline_lang_generator
from apps.translator_bot.functions import set_lang, save_conversation
from apps.translator_bot.models import TranslatorUser
from apps.translator_bot.translate_integrations import translate_text_with_lang
from apps.translator_bot.user_get_or_create import translator_user
from utils.decarators import get_member

logger = logging.getLogger(__name__)


@get_member
@translator_user
async def start(update: Update, context: CallbackContext, *args, **kwargs):
    if update.callback_query:
        await update.callback_query.edit_message_text(
            "Welcome to the translator bot. Please select your native language.",
            reply_markup=language_list_keyboard("native"))
    else:
        await update.message.reply_text("Welcome to the translator bot. Please select your native language.",
                                        reply_markup=language_list_keyboard("native"))


@get_member
@translator_user
async def change_native_lang(update: Update, context: CallbackContext, translator_user: TranslatorUser, *args,
                             **kwargs):
    if update.callback_query:
        await update.callback_query.edit_message_text(
            "Please select your native language.",
            reply_markup=language_list_keyboard("target"))
    else:
        await update.message.reply_text("Welcome to the translator bot. Please select your native language.",
                                        reply_markup=language_list_keyboard("target"))


@get_member
@translator_user
async def settings_user(update: Update, context: CallbackContext, translator_user: TranslatorUser, *args, **kwargs):
    native_lang, target_lang = translator_user.native_language, translator_user.target_language
    native_lang_name = next((item["name"] for item in language_list if item["id"] == native_lang), None)
    target_lang_name = next((item["name"] for item in language_list if item["id"] == target_lang), None)
    print(update)

    if update.message and update.message.entities and update.message.entities[0].type == "bot_command":
        if update.callback_query:
            await update.callback_query.edit_message_text(
                f"Your  language is {native_lang_name} => {target_lang_name}",
                reply_markup=inline_lang_generator(native_lang, target_lang))
        else:
            await update.message.reply_text(
                f"Your  language is {native_lang_name} => {target_lang_name}",
                reply_markup=inline_lang_generator(native_lang, target_lang))
    if  update.callback_query:
        query = update.callback_query
        query_data = update.callback_query.data
        if query_data.startswith("change_lang_"):
            type_lang = query_data.split("_")[-1]
            if type_lang == "native":
                await query.edit_message_text(
                    f"Can you select your native language?",
                    reply_markup=language_list_keyboard("reset_native"))
            if type_lang == "target":
                await query.edit_message_text(
                    f"Can you select your target language?",
                    reply_markup=language_list_keyboard("reset_target"))
        if query_data.startswith("language_reset_native"):
            lang = query.data.split("language_reset_native_")[1]
            await set_lang(translator_user, lang, True)
            native_lang, target_lang = translator_user.native_language, translator_user.target_language
            native_lang_name = next((item["name"] for item in language_list if item["id"] == native_lang), None)
            target_lang_name = next((item["name"] for item in language_list if item["id"] == target_lang), None)
            await update.callback_query.edit_message_text(
                f"Your  language is {native_lang_name} => {target_lang_name}",
                reply_markup=inline_lang_generator(native_lang, target_lang))

        if query_data.startswith("language_reset_target"):
            lang = query.data.split("language_reset_target_")[1]
            await set_lang(translator_user, lang, False)
            native_lang, target_lang = translator_user.native_language, translator_user.target_language
            native_lang_name = next((item["name"] for item in language_list if item["id"] == native_lang), None)
            target_lang_name = next((item["name"] for item in language_list if item["id"] == target_lang), None)
            await update.callback_query.edit_message_text(
                f"Your  language is {native_lang_name} => {target_lang_name}",
                reply_markup=inline_lang_generator(native_lang, target_lang))
    else:
        await update.message.reply_text(
            f"Your  language is {native_lang_name} => {target_lang_name}",
            reply_markup=inline_lang_generator(native_lang, target_lang))

@get_member
@translator_user
async def set_native_lang(update: Update, context: CallbackContext, translator_user: TranslatorUser,
                          user: TelegramProfile, *args, **kwargs):
    print("set_native_lang")
    print(translator_user)
    print(update.callback_query.data.split("_")[-1])
    query = update.callback_query
    lang = query.data.split("_")[-1]
    lang_name = next((item["name"] for item in language_list if item["id"] == lang), None)
    await set_lang(translator_user, lang, True)
    if lang_name:
        await query.edit_message_text("Native language has been set to " + lang_name,
                                      reply_markup=language_list_keyboard("target"))
        await query.answer("Language has been set to " + lang_name)
    else:
        await query.message.reply_text("Language not found.")
        await query.answer("Language not found.")
@get_member
@translator_user
async def set_target_lang(update: Update, context: CallbackContext, translator_user: TranslatorUser, *args, **kwargs):
    query = update.callback_query
    lang = query.data.split("_")[-1]
    lang_name = next((item["name"] for item in language_list if item["id"] == lang), None)
    await set_lang(translator_user, lang, False)

    if lang_name:
        await query.edit_message_text(f"Target language has been set to {lang_name} , please send word or sentece!")
        await query.answer("Language has been set to " + lang_name)
    else:
        await query.message.reply_text("Language not found.")
        await query.answer("Language not found.")


@get_member
@translator_user
async def translator(update: Update, context: CallbackContext, translator_user: TranslatorUser, *args, **kwargs):
    msg = update.message.text
    native_lang, target_lang = translator_user.native_language, translator_user.target_language
    word = await translate_text_with_lang(msg, native_lang, target_lang)
    await save_conversation(translator_user, msg, word.translated_text, native_lang, target_lang)
    buttons = ["Change Language", "History conversation", "About", "Restart"]
    reply_markup = generate_keyboard(buttons)
    await update.message.reply_text(word.translated_text,reply_markup=reply_markup)
