
import logging
import asyncio
from django.utils import timezone
from datetime import datetime
from apps.chatgpt.functions import *
from apps.bot.models import  TelegramProfile
import telegram
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    CallbackContext,
)
from telegram.constants import ParseMode
from utils.decarators import get_member
from .config import *
from .openai_utils import *
from .database import Database as db
import apps.chatgpt.models as model

# setup
logger = logging.getLogger(__name__)

user_semaphores = {}
user_tasks = {}

HELP_MESSAGE = """Commands:
⚪ /retry – Regenerate last bot answer
⚪ /new – Start new dialog
⚪ /mode – Select chat mode
⚪ /settings – Show settings
⚪ /balance – Show balance
⚪ /help – Show help

🎨 Generate images from text prompts in <b>👩‍🎨 Artist</b> /mode
👥 Add bot to <b>group chat</b>: /help_group_chat
🎤 You can send <b>Voice Messages</b> instead of text
"""

HELP_GROUP_CHAT_MESSAGE = """You can add bot to any <b>group chat</b> to help and entertain its participants!

Instructions (see <b>video</b> below):
1. Add the bot to the group chat
2. Make it an <b>admin</b>, so that it can see messages (all other rights can be restricted)
3. You're awesome!

To get a reply from the bot in the chat – @ <b>tag</b> it or <b>reply</b> to its message.
For example: "{bot_username} write a poem about Telegram"
"""


def split_text_into_chunks(text, chunk_size):
    for i in range(0, len(text), chunk_size):
        yield text[i:i + chunk_size]


async def register_user_if_not_exists(update: Update, context: CallbackContext, telegram_id: int):
    user = await get_user_by_id(telegram_id)

    if user.current_model is None:
        db.start_new_dialog(telegram_id,context.bot.username)

    if telegram_id not in user_semaphores:
        user_semaphores[telegram_id] = asyncio.Semaphore(1)

    if user.current_model is None:
        user.current_model = model.GptModels.objects.first(), "gpt-3.5-turbo"

    # back compatibility for n_used_tokens field
    n_used_tokens = user.n_used_tokens
    if isinstance(n_used_tokens, int) or isinstance(n_used_tokens, float):  # old format
        new_n_used_tokens = {
            "gpt-3.5-turbo": {
                "n_input_tokens": 0,
                "n_output_tokens": n_used_tokens
            }
        }
        user.n_used_tokens = new_n_used_tokens

    # voice message transcription
    if user.n_transcribed_seconds is None:
        user.n_transcribed_seconds = 0.0

    # image generation
    if user.n_generated_images is None:
        user.n_generated_images = 0


async def is_bot_mentioned(update: Update, context: CallbackContext):
    try:
        message = update.message

        if message.chat.type == "private":
            return True

        if message.text is not None and ("@" + context.bot.username) in message.text:
            return True

        if message.reply_to_message is not None:
            if message.reply_to_message.from_user.id == context.bot.id:
                return True
    except:
        return True
    else:
        return False


@get_member
async def start_handle(update: Update, context: CallbackContext, tg_user: TelegramProfile):
    try:
        user_exists = await check_user_exists(tg_user)
        logger.info("User exists: %s", user_exists)

        if user_exists:
            user = await get_user(tg_user)
            logger.info("Retrieved existing user: %s", user)
        else:
            user = await create_user(tg_user)
            logger.info("Created new user: %s", user)

        if user is not None:
            user.last_interaction = datetime.now()
            await save_user_async(user)

    except Exception as e:
        logger.error("Error in start_handle: %s", e)

    reply_text = f"Hi! I'm <b>ChatGPT</b> bot implemented with OpenAI API 🤖\n\n{HELP_MESSAGE}"
    await update.message.reply_text(reply_text, parse_mode=ParseMode.HTML)
    await show_chat_modes_handle(update, context)



async def message_handle(update: Update, context: CallbackContext, message=None, use_new_dialog_timeout=True):
    # check if bot was mentioned (for group chats)
    if not await is_bot_mentioned(update, context):
        return
    print("check if bot was mentioned...")
    # check if message is edited
    if update.edited_message is not None:
        await edited_message_handle(update, context)
        return
    print("check if message is edited...")
    _message = message or update.message.text
    print(_message)
    # remove bot mention (in group chats)
    if update.message.chat.type != "private":
        _message = _message.replace("@" + context.bot.username, "").strip()
        print("private:",_message)
    await register_user_if_not_exists(update, context, update.message.from_user.id)
    if await is_previous_message_not_answered_yet(update, context): return

    user_id = update.effective_user.id
    user = await get_user_by_id(user_id)
    chat_mode = user.current_chat_mode

    # if chat_mode == "artist":
    #     await generate_image_handle(update, context, message=message)
    #     return

    async def message_handle_fn():
        user_id = update.effective_user.id
        user = await get_user_by_id(user_id)
        current_model = user.current_model

        # new dialog timeout
        if use_new_dialog_timeout:
            current_time = timezone.now()

            # Check if user.last_interaction is not already an offset-aware datetime
            if not timezone.is_aware(user.last_interaction):
                user.last_interaction = timezone.make_aware(user.last_interaction)

            if (current_time - user.last_interaction).seconds > new_dialog_timeout:
                await db.start_new_dialog(user_id,context.bot.username)
                chat_mode_name = await get_chat_mode_name(user_id)
                await update.message.reply_text(
                    f"Starting new dialog due to timeout (<b>{chat_mode_name}</b> mode) ✅",
                    parse_mode=ParseMode.HTML)

        await database_sync_to_async(user.save)()

        # in case of CancelledError
        n_input_tokens, n_output_tokens = 0, 0

        try:
            # send placeholder message to user
            placeholder_message = await update.message.reply_text("...")

            # send typing action
            await update.message.chat.send_action(action="typing")

            if _message is None:
                await update.message.reply_text("🥲 You sent <b>empty message</b>. Please, try again!",
                                                parse_mode=ParseMode.HTML)
                return
            print("message_handle_fn", user_id)
            usename_bot= context.bot.username
            print(usename_bot)
            dialog_messages = await db.get_dialog_messages(user_id,usename_bot,update.message.text)
            print("dialog_messages: ",dialog_messages)
            parse_mode = {
                "html": ParseMode.HTML,
                "markdown": ParseMode.MARKDOWN
            }

            chatgpt_instance = ChatGPT(model=current_model)
            if enable_message_streaming:
                gen = chatgpt_instance.send_message_stream(_message, dialog_messages=dialog_messages,
                                                           chat_mode=chat_mode)
            else:
                answer, (
                    n_input_tokens,
                    n_output_tokens), n_first_dialog_messages_removed = await chatgpt_instance.send_message(
                    _message,
                    dialog_messages=dialog_messages,
                    chat_mode=chat_mode
                )

                async def fake_gen():
                    yield "finished", answer, (n_input_tokens, n_output_tokens), n_first_dialog_messages_removed

                gen = fake_gen()

            prev_answer = ""
            async for gen_item in gen:
                status, answer, (n_input_tokens, n_output_tokens), n_first_dialog_messages_removed = gen_item

                answer = answer[:4096]  # telegram message limit

                # update only when 100 new symbols are ready
                if abs(len(answer) - len(prev_answer)) < 100 and status != "finished":
                    continue

                try:
                    await context.bot.edit_message_text(answer, chat_id=placeholder_message.chat_id,
                                                        message_id=placeholder_message.message_id,
                                                        parse_mode=parse_mode)
                except telegram.error.BadRequest as e:
                    if str(e).startswith("Message is not modified"):
                        continue
                    else:
                        await context.bot.edit_message_text(answer, chat_id=placeholder_message.chat_id,
                                                            message_id=placeholder_message.message_id)

                await asyncio.sleep(0.01)  # wait a bit to avoid flooding

                prev_answer = answer

            # update user data
            new_dialog_message = {"user": _message, "bot": answer, "date": datetime.now()},

            await db.set_dialog_messages(
                user_id,
                new_dialog_message,
                context.bot.username
            )

            db.update_n_used_tokens(user_id, current_model, n_input_tokens, n_output_tokens)

        except asyncio.CancelledError:
            # note: intermediate token updates only work when enable_message_streaming=True (  yml)
            db.update_n_used_tokens(user_id, current_model, n_input_tokens, n_output_tokens)
            raise

        except Exception as e:
            error_text = f"Something went wrong during completion. Reason: {e}"
            logger.error(error_text)
            await update.message.reply_text(error_text)
            return

        # send message if some messages were removed from the context
        if n_first_dialog_messages_removed > 0:
            if n_first_dialog_messages_removed == 1:
                text = "✍️ <i>Note:</i> Your current dialog is too long, so your <b>first message</b> was removed from the context.\n Send /new command to start new dialog"
            else:
                text = f"✍️ <i>Note:</i> Your current dialog is too long, so <b>{n_first_dialog_messages_removed} first messages</b> were removed from the context.\n Send /new command to start new dialog"
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)

    async with user_semaphores[user_id]:
        task = asyncio.create_task(message_handle_fn())
        user_tasks[user_id] = task

        try:
            await task
        except asyncio.CancelledError:
            await update.message.reply_text("✅ Canceled", parse_mode=ParseMode.HTML)
        else:
            pass
        finally:
            if user_id in user_tasks:
                del user_tasks[user_id]


# async def help_handle(update: Update, context: CallbackContext):
#     user_id = update.message.from_user.id
#     db.set_user_attribute(user_id, "last_interaction", datetime.now())
#     await update.message.reply_text(HELP_MESSAGE, parse_mode=ParseMode.HTML)
#
#
# async def help_group_chat_handle(update: Update, context: CallbackContext):
#     await register_user_if_not_exists(update, context, update.message.from_user)
#     user_id = update.message.from_user.id
#     db.set_user_attribute(user_id, "last_interaction", datetime.now())
#
#     text = HELP_GROUP_CHAT_MESSAGE.format(bot_username="@" + context.bot.username)
#
#     await update.message.reply_text(text, parse_mode=ParseMode.HTML)
#     await update.message.reply_video(help_group_chat_video_path)
#
#
# async def retry_handle(update: Update, context: CallbackContext):
#     await register_user_if_not_exists(update, context, update.message.from_user)
#     if await is_previous_message_not_answered_yet(update, context): return
#
#     user_id = update.message.from_user.id
#     db.set_user_attribute(user_id, "last_interaction", datetime.now())
#
#     dialog_messages = db.get_dialog_messages(user_id)
#     if len(dialog_messages) == 0:
#         await update.message.reply_text("No message to retry 🤷‍♂️")
#         return
#
#     last_dialog_message = dialog_messages.pop()
#     db.set_dialog_messages(user_id, dialog_messages, dialog_id=None)  # last message was removed from the context
#
#     await message_handle(update, context, message=last_dialog_message["user"], use_new_dialog_timeout=False)
#

async def is_previous_message_not_answered_yet(update: Update, context: CallbackContext):
    await register_user_if_not_exists(update, context, update.effective_user.id)

    user_id = update.message.from_user.id
    if user_semaphores[user_id].locked():
        text = "⏳ Please <b>wait</b> for a reply to the previous message\n"
        text += "Or you can /cancel it"
        await update.message.reply_text(text, reply_to_message_id=update.message.id, parse_mode=ParseMode.HTML)
        return True
    else:
        return False


# async def voice_message_handle(update: Update, context: CallbackContext):
#     # check if bot was mentioned (for group chats)
#     if not await is_bot_mentioned(update, context):
#         return
#
#     await register_user_if_not_exists(update, context, update.message.from_user)
#     if await is_previous_message_not_answered_yet(update, context): return
#
#     user_id = update.message.from_user.id
#     db.set_user_attribute(user_id, "last_interaction", datetime.now())
#
#     voice = update.message.voice
#     voice_file = await context.bot.get_file(voice.file_id)
#
#     # store file in memory, not on disk
#     buf = io.BytesIO()
#     await voice_file.download_to_memory(buf)
#     buf.name = "voice.oga"  # file extension is required
#     buf.seek(0)  # move cursor to the beginning of the buffer
#
#     transcribed_text = await transcribe_audio(buf)
#     text = f"🎤: <i>{transcribed_text}</i>"
#     await update.message.reply_text(text, parse_mode=ParseMode.HTML)
#
#     # update n_transcribed_seconds
#     db.set_user_attribute(user_id, "n_transcribed_seconds",
#                           voice.duration + db.get_user_attribute(user_id, "n_transcribed_seconds"))
#
#     await message_handle(update, context, message=transcribed_text)


# async def generate_image_handle(update: Update, context: CallbackContext, message=None):
#     await register_user_if_not_exists(update, context, update.message.from_user)
#     if await is_previous_message_not_answered_yet(update, context): return
#
#     user_id = update.message.from_user.id
#     db.set_user_attribute(user_id, "last_interaction", datetime.now())
#
#     await update.message.chat.send_action(action="upload_photo")
#
#     message = message or update.message.text
#
#     try:
#         image_urls = await generate_images(message, n_images=return_n_generated_images, size=image_size)
#     except openai.error.InvalidRequestError as e:
#         if str(e).startswith("Your request was rejected as a result of our safety system"):
#             text = "🥲 Your request <b>doesn't comply</b> with OpenAI's usage policies.\nWhat did you write there, huh?"
#             await update.message.reply_text(text, parse_mode=ParseMode.HTML)
#             return
#         else:
#             raise
#
#     # token usage
#     db.set_user_attribute(user_id, "n_generated_images",
#                           return_n_generated_images + db.get_user_attribute(user_id, "n_generated_images"))
#
#     for i, image_url in enumerate(image_urls):
#         await update.message.chat.send_action(action="upload_photo")
#         await update.message.reply_photo(image_url, parse_mode=ParseMode.HTML)
#
#
# async def new_dialog_handle(update: Update, context: CallbackContext):
#     await register_user_if_not_exists(update, context, update.message.from_user)
#     if await is_previous_message_not_answered_yet(update, context): return
#
#     user_id = update.message.from_user.id
#     db.set_user_attribute(user_id, "last_interaction", datetime.now())
#
#     db.start_new_dialog(user_id)
#     await update.message.reply_text("Starting new dialog ✅")
#
#     chat_mode = db.get_user_attribute(user_id, "current_chat_mode")
#     await update.message.reply_text(f"{chat_modes[chat_mode]['welcome_message']}", parse_mode=ParseMode.HTML)
#
#
# async def cancel_handle(update: Update, context: CallbackContext):
#     await register_user_if_not_exists(update, context, update.message.from_user)
#
#     user_id = update.message.from_user.id
#     db.set_user_attribute(user_id, "last_interaction", datetime.now())
#
#     if user_id in user_tasks:
#         task = user_tasks[user_id]
#         task.cancel()
#     else:
#         await update.message.reply_text("<i>Nothing to cancel...</i>", parse_mode=ParseMode.HTML)


def get_chat_mode_menu(page_index: int):
    n_chat_modes_per_page = 5
    text = f"Select <b>chat mode</b> ({len(chat_modes)} modes available):"

    # buttons
    chat_mode_keys = list(chat_modes.keys())
    page_chat_mode_keys = chat_mode_keys[page_index * n_chat_modes_per_page:(page_index + 1) * n_chat_modes_per_page]

    keyboard = []
    for chat_mode_key in page_chat_mode_keys:
        name = chat_modes[chat_mode_key]["name"]
        keyboard.append([InlineKeyboardButton(name, callback_data=f"set_chat_mode|{chat_mode_key}")])

    # pagination
    if len(chat_mode_keys) > n_chat_modes_per_page:
        is_first_page = (page_index == 0)
        is_last_page = ((page_index + 1) * n_chat_modes_per_page >= len(chat_mode_keys))

        if is_first_page:
            keyboard.append([
                InlineKeyboardButton("»", callback_data=f"show_chat_modes|{page_index + 1}")
            ])
        elif is_last_page:
            keyboard.append([
                InlineKeyboardButton("«", callback_data=f"show_chat_modes|{page_index - 1}"),
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("«", callback_data=f"show_chat_modes|{page_index - 1}"),
                InlineKeyboardButton("»", callback_data=f"show_chat_modes|{page_index + 1}")
            ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    return text, reply_markup


@get_member
async def show_chat_modes_handle(update: Update, context: CallbackContext, tg_user: TelegramProfile):
    await register_user_if_not_exists(update, context, tg_user.telegram_id)
    if await is_previous_message_not_answered_yet(update, context): return

    print(tg_user)
    print(tg_user.telegram_id)
    user_id = tg_user.telegram_id
    try:
        user_exists = await check_user_exists(tg_user)

        if user_exists:
            user = await get_user(tg_user)
        else:
            user = await create_user(tg_user)
    except Exception as e:
        logger.error(e)
        return
    user.last_interaction = datetime.now()
    await database_sync_to_async(user.save)()

    text, reply_markup = get_chat_mode_menu(0)
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)


async def show_chat_modes_callback_handle(update: Update, context: CallbackContext):
    await register_user_if_not_exists(update.callback_query, context, update.callback_query.from_user)
    if await is_previous_message_not_answered_yet(update.callback_query, context): return

    user_id = update.callback_query.from_user.id
    db.set_user_attribute(user_id, "last_interaction", datetime.now())

    query = update.callback_query
    await query.answer()

    page_index = int(query.data.split("|")[1])
    if page_index < 0:
        return

    text, reply_markup = get_chat_mode_menu(page_index)
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except telegram.error.BadRequest as e:
        if str(e).startswith("Message is not modified"):
            pass


# async def set_chat_mode_handle(update: Update, context: CallbackContext):
#     await register_user_if_not_exists(update.callback_query, context, update.callback_query.from_user)
#     user_id = update.callback_query.from_user.id
#
#     query = update.callback_query
#     await query.answer()
#
#     chat_mode = query.data.split("|")[1]
#
#     db.set_user_attribute(user_id, "current_chat_mode", chat_mode)
#     db.start_new_dialog(user_id)
#
#     await context.bot.send_message(
#         update.callback_query.message.chat.id,
#         f"{chat_modes[chat_mode]['welcome_message']}",
#         parse_mode=ParseMode.HTML
#     )


# def get_settings_menu(user_id: int):
#     current_model = db.get_user_attribute(user_id, "current_model")
#     text = models["info"][current_model]["description"]
#
#     text += "\n\n"
#     score_dict = models["info"][current_model]["scores"]
#     for score_key, score_value in score_dict.items():
#         text += "🟢" * score_value + "⚪️" * (5 - score_value) + f" – {score_key}\n\n"
#
#     text += "\nSelect <b>model</b>:"
#
#     # buttons to choose models
#     buttons = []
#     for model_key in models["available_text_models"]:
#         title = models["info"][model_key]["name"]
#         if model_key == current_model:
#             title = "✅ " + title
#
#         buttons.append(
#             InlineKeyboardButton(title, callback_data=f"set_settings|{model_key}")
#         )
#     reply_markup = InlineKeyboardMarkup([buttons])
#
#     return text, reply_markup
#
#
# async def settings_handle(update: Update, context: CallbackContext):
#     await register_user_if_not_exists(update, context, update.message.from_user)
#     if await is_previous_message_not_answered_yet(update, context): return
#
#     user_id = update.message.from_user.id
#     db.set_user_attribute(user_id, "last_interaction", datetime.now())
#
#     text, reply_markup = get_settings_menu(user_id)
#     await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
#
#
# async def set_settings_handle(update: Update, context: CallbackContext):
#     await register_user_if_not_exists(update.callback_query, context, update.callback_query.from_user)
#     user_id = update.callback_query.from_user.id
#
#     query = update.callback_query
#     await query.answer()
#
#     _, model_key = query.data.split("|")
#     db.set_user_attribute(user_id, "current_model", model_key)
#     db.start_new_dialog(user_id)
#
#     text, reply_markup = get_settings_menu(user_id)
#     try:
#         await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
#     except telegram.error.BadRequest as e:
#         if str(e).startswith("Message is not modified"):
#             pass


# async def show_balance_handle(update: Update, context: CallbackContext):
#     await register_user_if_not_exists(update, context, update.message.from_user)
#
#     user_id = update.message.from_user.id
#     db.set_user_attribute(user_id, "last_interaction", datetime.now())
#
#     # count total usage statistics
#     total_n_spent_dollars = 0
#     total_n_used_tokens = 0
#
#     n_used_tokens_dict = db.get_user_attribute(user_id, "n_used_tokens")
#     n_generated_images = db.get_user_attribute(user_id, "n_generated_images")
#     n_transcribed_seconds = db.get_user_attribute(user_id, "n_transcribed_seconds")
#
#     details_text = "🏷️ Details:\n"
#     for model_key in sorted(n_used_tokens_dict.keys()):
#         n_input_tokens, n_output_tokens = n_used_tokens_dict[model_key]["n_input_tokens"], \
#             n_used_tokens_dict[model_key]["n_output_tokens"]
#         total_n_used_tokens += n_input_tokens + n_output_tokens
#
#         n_input_spent_dollars = models["info"][model_key]["price_per_1000_input_tokens"] * (n_input_tokens / 1000)
#         n_output_spent_dollars = models["info"][model_key]["price_per_1000_output_tokens"] * (n_output_tokens / 1000)
#         total_n_spent_dollars += n_input_spent_dollars + n_output_spent_dollars
#
#         details_text += f"- {model_key}: <b>{n_input_spent_dollars + n_output_spent_dollars:.03f}$</b> / <b>{n_input_tokens + n_output_tokens} tokens</b>\n"
#
#     # image generation
#     image_generation_n_spent_dollars = models["info"]["dalle-2"]["price_per_1_image"] * n_generated_images
#     if n_generated_images != 0:
#         details_text += f"- DALL·E 2 (image generation): <b>{image_generation_n_spent_dollars:.03f}$</b> / <b>{n_generated_images} generated images</b>\n"
#
#     total_n_spent_dollars += image_generation_n_spent_dollars
#
#     # voice recognition
#     voice_recognition_n_spent_dollars = models["info"]["whisper"]["price_per_1_min"] * (n_transcribed_seconds / 60)
#     if n_transcribed_seconds != 0:
#         details_text += f"- Whisper (voice recognition): <b>{voice_recognition_n_spent_dollars:.03f}$</b> / <b>{n_transcribed_seconds:.01f} seconds</b>\n"
#
#     total_n_spent_dollars += voice_recognition_n_spent_dollars
#
#     text = f"You spent <b>{total_n_spent_dollars:.03f}$</b>\n"
#     text += f"You used <b>{total_n_used_tokens}</b> tokens\n\n"
#     text += details_text
#
#     await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def edited_message_handle(update: Update, context: CallbackContext):
    if update.edited_message.chat.type == "private":
        text = "🥲 Unfortunately, message <b>editing</b> is not supported"
        await update.edited_message.reply_text(text, parse_mode=ParseMode.HTML)

#
# async def error_handle(update: Update, context: CallbackContext) -> None:
#     logger.error(msg="Exception while handling an update:", exc_info=context.error)
#
#     try:
#         # collect error message
#         tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
#         tb_string = "".join(tb_list)
#         update_str = update.to_dict() if isinstance(update, Update) else str(update)
#         message = (
#             f"An exception was raised while handling an update\n"
#             f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
#             "</pre>\n\n"
#             f"<pre>{html.escape(tb_string)}</pre>"
#         )
#
#         # split text into multiple messages due to 4096 character limit
#         for message_chunk in split_text_into_chunks(message, 4096):
#             try:
#                 await context.bot.send_message(update.effective_chat.id, message_chunk, parse_mode=ParseMode.HTML)
#             except telegram.error.BadRequest:
#                 # answer has invalid characters, so we send it without parse_mode
#                 await context.bot.send_message(update.effective_chat.id, message_chunk)
#     except:
#         await context.bot.send_message(update.effective_chat.id, "Some error in error handler")
