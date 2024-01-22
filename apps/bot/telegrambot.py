import datetime
import logging
from dotenv import load_dotenv
import telegram
from django.conf import settings
from django.core.exceptions import BadRequest
from django.utils import timezone
from telegram import Update
from telegram.ext import CallbackContext, ContextTypes
from django.utils.translation import gettext_lazy as _, activate
from apps.chatgpt.openai_helper import OpenAIHelper, default_max_tokens, are_functions_available
from apps.bot import models
from apps.chatgpt import main
from apps.chatgpt.plugin_manager import PluginManager
from utils.decarators import get_member


#######
# from __future__ import annotations

import asyncio
import logging
import os
import io

from uuid import uuid4
from telegram import BotCommandScopeAllGroupChats, Update, constants
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle
from telegram import InputTextMessageContent, BotCommand
from telegram.error import RetryAfter, TimedOut, BadRequest
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, \
    filters, InlineQueryHandler, CallbackQueryHandler, Application, ContextTypes, CallbackContext

from pydub import AudioSegment
from PIL import Image

from apps.chatgpt.utils import is_group_chat, get_thread_id, wrap_with_indicator, split_into_chunks, \
    edit_message_with_retry, get_stream_cutoff_values, is_allowed, get_remaining_budget, is_admin, is_within_budget, \
    get_reply_to_message_id, add_chat_request_to_usage_tracker, error_handler, is_direct_result, handle_direct_result, \
    cleanup_intermediate_files
from apps.chatgpt.openai_helper import OpenAIHelper, localized_text
from apps.chatgpt.usage_tracker import UsageTracker
from telegram import Message, MessageEntity, Update, ChatMember, constants


logger = logging.getLogger(__name__)

def message_text(message: Message) -> str:
    """
    Returns the text of a message, excluding any bot commands.
    """
    message_txt = message.text
    if message_txt is None:
        return ''

    for _, text in sorted(message.parse_entities([MessageEntity.BOT_COMMAND]).items(),
                          key=(lambda item: item[0].offset)):
        message_txt = message_txt.replace(text, '').strip()

    return message_txt if len(message_txt) > 0 else ''


@get_member
async def start(update: Update, context: CallbackContext, tg_user: models.TelegramProfile):
    """Send a message asynchronously when the command /start is issued."""


    try:
        await update.message.reply_text("Assalomu alaykum, bot ishladi")
    except Exception as e:
        logger.error(f"Error in start command: {e}")

@get_member
async def prompt(update: Update, context: CallbackContext, tg_user: models.TelegramProfile):
    """Send a message asynchronously when the command /start is issued."""



    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    prompt = message_text(update.message)

    print(prompt)
    await update.effective_message.reply_chat_action(
        action=constants.ChatAction.TYPING,
        message_thread_id=get_thread_id(update)
    )
    load_dotenv()

    # Setup logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    # Check if the required environment variables are set
    required_values = ['OPENAI_API_KEY']

    # Setup configurations
    model = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
    functions_available = are_functions_available(model=model)
    max_tokens_default = default_max_tokens(model=model)
    config = {
        'token': "6642950059:AAGex0ISI9G3NyFInA3YJ5kn_Z_3D_SMgFM",
        'admin_user_ids': os.environ.get('ADMIN_USER_IDS', '-'),
        'allowed_user_ids': os.environ.get('ALLOWED_TELEGRAM_USER_IDS', '*'),
        'enable_quoting': os.environ.get('ENABLE_QUOTING', 'true').lower() == 'true',
        'enable_image_generation': os.environ.get('ENABLE_IMAGE_GENERATION', 'true').lower() == 'true',
        'enable_transcription': os.environ.get('ENABLE_TRANSCRIPTION', 'true').lower() == 'true',
        'enable_vision': os.environ.get('ENABLE_VISION', 'true').lower() == 'true',
        'enable_tts_generation': os.environ.get('ENABLE_TTS_GENERATION', 'true').lower() == 'true',
        'budget_period': os.environ.get('BUDGET_PERIOD', 'monthly').lower(),
        'user_budgets': os.environ.get('USER_BUDGETS', os.environ.get('MONTHLY_USER_BUDGETS', '*')),
        'guest_budget': float(os.environ.get('GUEST_BUDGET', os.environ.get('MONTHLY_GUEST_BUDGET', '100.0'))),
        'stream': os.environ.get('STREAM', 'true').lower() == 'true',
        'proxy': os.environ.get('PROXY', None) or os.environ.get('TELEGRAM_PROXY', None),
        'voice_reply_transcript': os.environ.get('VOICE_REPLY_WITH_TRANSCRIPT_ONLY', 'false').lower() == 'true',
        'voice_reply_prompts': os.environ.get('VOICE_REPLY_PROMPTS', '').split(';'),
        'ignore_group_transcriptions': os.environ.get('IGNORE_GROUP_TRANSCRIPTIONS', 'true').lower() == 'true',
        'ignore_group_vision': os.environ.get('IGNORE_GROUP_VISION', 'true').lower() == 'true',
        'group_trigger_keyword': os.environ.get('GROUP_TRIGGER_KEYWORD', ''),
        'token_price': float(os.environ.get('TOKEN_PRICE', 0.002)),
        'image_prices': [float(i) for i in os.environ.get('IMAGE_PRICES', "0.016,0.018,0.02").split(",")],
        'vision_token_price': float(os.environ.get('VISION_TOKEN_PRICE', '0.01')),
        'image_receive_mode': os.environ.get('IMAGE_FORMAT', "photo"),
        'tts_model': os.environ.get('TTS_MODEL', 'tts-1'),
        'tts_prices': [float(i) for i in os.environ.get('TTS_PRICES', "0.015,0.030").split(",")],
        'transcription_price': float(os.environ.get('TRANSCRIPTION_PRICE', 0.006)),
        'bot_language': os.environ.get('BOT_LANGUAGE', 'en'),
    }
    openai_config = {
        'api_key': os.environ['OPENAI_API_KEY'],
        'show_usage': os.environ.get('SHOW_USAGE', 'false').lower() == 'true',
        'stream': os.environ.get('STREAM', 'true').lower() == 'true',
        'proxy': os.environ.get('PROXY', None) or os.environ.get('OPENAI_PROXY', None),
        'max_history_size': int(os.environ.get('MAX_HISTORY_SIZE', 15)),
        'max_conversation_age_minutes': int(os.environ.get('MAX_CONVERSATION_AGE_MINUTES', 180)),
        'assistant_prompt': os.environ.get('ASSISTANT_PROMPT', 'You are a helpful assistant.'),
        'max_tokens': int(os.environ.get('MAX_TOKENS', max_tokens_default)),
        'n_choices': int(os.environ.get('N_CHOICES', 1)),
        'temperature': float(os.environ.get('TEMPERATURE', 1.0)),
        'image_model': os.environ.get('IMAGE_MODEL', 'dall-e-2'),
        'image_quality': os.environ.get('IMAGE_QUALITY', 'standard'),
        'image_style': os.environ.get('IMAGE_STYLE', 'vivid'),
        'image_size': os.environ.get('IMAGE_SIZE', '512x512'),
        'model': model,
        'enable_functions': os.environ.get('ENABLE_FUNCTIONS', str(functions_available)).lower() == 'true',
        'functions_max_consecutive_calls': int(os.environ.get('FUNCTIONS_MAX_CONSECUTIVE_CALLS', 10)),
        'presence_penalty': float(os.environ.get('PRESENCE_PENALTY', 0.0)),
        'frequency_penalty': float(os.environ.get('FREQUENCY_PENALTY', 0.0)),
        'bot_language': os.environ.get('BOT_LANGUAGE', 'en'),
        'show_plugins_used': os.environ.get('SHOW_PLUGINS_USED', 'false').lower() == 'true',
        'whisper_prompt': os.environ.get('WHISPER_PROMPT', ''),
        'vision_model': os.environ.get('VISION_MODEL', 'gpt-4-vision-preview'),
        'enable_vision_follow_up_questions': os.environ.get('ENABLE_VISION_FOLLOW_UP_QUESTIONS', 'true').lower() == 'true',
        'vision_prompt': os.environ.get('VISION_PROMPT', 'What is in this image'),
        'vision_detail': os.environ.get('VISION_DETAIL', 'auto'),
        'vision_max_tokens': int(os.environ.get('VISION_MAX_TOKENS', '300')),
        'tts_model': os.environ.get('TTS_MODEL', 'tts-1'),
        'tts_voice': os.environ.get('TTS_VOICE', 'alloy'),
    }
    if openai_config['enable_functions'] and not functions_available:
        logging.error(f'ENABLE_FUNCTIONS is set to true, but the model {model} does not support it. '
                        f'Please set ENABLE_FUNCTIONS to false or use a model that supports it.')
        exit(1)
    if os.environ.get('MONTHLY_USER_BUDGETS') is not None:
        logging.warning('The environment variable MONTHLY_USER_BUDGETS is deprecated. '
                        'Please use USER_BUDGETS with BUDGET_PERIOD instead.')
    if os.environ.get('MONTHLY_GUEST_BUDGET') is not None:
        logging.warning('The environment variable MONTHLY_GUEST_BUDGET is deprecated. '
                        'Please use GUEST_BUDGET with BUDGET_PERIOD instead.')
    plugin_config = {
        'plugins': os.environ.get('PLUGINS', '').split(',')
    }

    # Setup and run ChatGPT and Telegram bot
    plugin_manager = PluginManager(config=plugin_config)
    openai=openai_helper = OpenAIHelper(config=openai_config, plugin_manager=plugin_manager)
    if is_group_chat(update):
        trigger_keyword = config['group_trigger_keyword']

        if prompt.lower().startswith(trigger_keyword.lower()) or update.message.text.lower().startswith('/chat'):
            if prompt.lower().startswith(trigger_keyword.lower()):
                prompt = prompt[len(trigger_keyword):].strip()

            if update.message.reply_to_message and \
                    update.message.reply_to_message.text and \
                    update.message.reply_to_message.from_user.id != context.bot.id:
                prompt = f'"{update.message.reply_to_message.text}" {prompt}'
        else:
            if update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id:
                logging.info('Message is a reply to the bot, allowing...')
            else:
                logging.warning('Message does not start with trigger keyword, ignoring...')
                return

    try:
        total_tokens = 0

        if config['stream']:
            await update.effective_message.reply_chat_action(
                action=constants.ChatAction.TYPING,
                message_thread_id=get_thread_id(update)
            )
            print("streaming", "query:", prompt)
            stream_response = openai.get_chat_response_stream(chat_id=chat_id, query=prompt)
            i = 0
            prev = ''
            sent_message = None
            backoff = 0
            stream_chunk = 0

            async for content, tokens in stream_response:
                if is_direct_result(content):
                    return await handle_direct_result(config, update, content)

                if len(content.strip()) == 0:
                    continue

                stream_chunks = split_into_chunks(content)
                if len(stream_chunks) > 1:
                    content = stream_chunks[-1]
                    if stream_chunk != len(stream_chunks) - 1:
                        stream_chunk += 1
                        try:
                            await edit_message_with_retry(context, chat_id, str(sent_message.message_id),
                                                          stream_chunks[-2])
                        except:
                            pass
                        try:
                            sent_message = await update.effective_message.reply_text(
                                message_thread_id=get_thread_id(update),
                                text=content if len(content) > 0 else "..."
                            )
                        except:
                            pass
                        continue

                cutoff = get_stream_cutoff_values(update, content)
                cutoff += backoff

                if i == 0:
                    try:
                        if sent_message is not None:
                            await context.bot.delete_message(chat_id=sent_message.chat_id,
                                                             message_id=sent_message.message_id)
                        sent_message = await update.effective_message.reply_text(
                            message_thread_id=get_thread_id(update),
                            reply_to_message_id=get_reply_to_message_id(config, update),
                            text=content,
                        )
                    except:
                        continue

                elif abs(len(content) - len(prev)) > cutoff or tokens != 'not_finished':
                    prev = content

                    try:
                        use_markdown = tokens != 'not_finished'
                        await edit_message_with_retry(context, chat_id, str(sent_message.message_id),
                                                      text=content, markdown=use_markdown)

                    except RetryAfter as e:
                        backoff += 5
                        await asyncio.sleep(e.retry_after)
                        continue

                    except TimedOut:
                        backoff += 5
                        await asyncio.sleep(0.5)
                        continue

                    except Exception:
                        backoff += 5
                        continue

                    await asyncio.sleep(0.01)

                i += 1
                if tokens != 'not_finished':
                    total_tokens = int(tokens)

        else:
            async def _reply():
                nonlocal total_tokens
                response, total_tokens = await openai.get_chat_response(chat_id=chat_id, query=prompt)

                if is_direct_result(response):
                    return await handle_direct_result(config, update, response)

                # Split into chunks of 4096 characters (Telegram's message limit)
                chunks = split_into_chunks(response)

                for index, chunk in enumerate(chunks):
                    try:
                        await update.effective_message.reply_text(
                            message_thread_id=get_thread_id(update),
                            reply_to_message_id=get_reply_to_message_id(config,
                                                                        update) if index == 0 else None,
                            text=chunk,
                            parse_mode=constants.ParseMode.MARKDOWN
                        )
                    except Exception:
                        try:
                            await update.effective_message.reply_text(
                                message_thread_id=get_thread_id(update),
                                reply_to_message_id=get_reply_to_message_id(config,
                                                                            update) if index == 0 else None,
                                text=chunk
                            )
                        except Exception as exception:
                            raise exception

            await wrap_with_indicator(update, context, _reply, constants.ChatAction.TYPING)
        #
        # add_chat_request_to_usage_tracker(usage, config, user_id, total_tokens)

    except Exception as e:
        logging.exception(e)
        await update.effective_message.reply_text(
            message_thread_id=get_thread_id(update),
            reply_to_message_id=get_reply_to_message_id(config, update),
            text=f"{localized_text('chat_fail', config['bot_language'])} {str(e)}",
            parse_mode=constants.ParseMode.MARKDOWN
        )