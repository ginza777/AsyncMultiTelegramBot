import logging
import uuid
from datetime import datetime

import environ
import openai
from asgiref.sync import sync_to_async
from telegram.constants import ParseMode

from apps.bot_main_setup.log_chat import send_msg_log
from apps.chatgpt_bot.function.functions import get_openai_key
from apps.chatgpt_bot.models import Dialog, Messages_dialog
from apps.chatgpt_bot.openai_integrations.token_calculator import num_tokens_from_messages

env = environ.Env()
environ.Env.read_env()

# logging
logger = logging.getLogger(__name__)


@sync_to_async
def delete_messages(token):
    Messages_dialog.objects.filter(msg_token=token).delete()


@sync_to_async
def create_msg(message, answer, user, input_tokens, output_tokens, random_token):
    print("create_msg: ", random_token, message)
    if Dialog.objects.filter(user=user, end=False).exists():
        dialog = Dialog.objects.filter(user=user, end=False).last()
        dialog.input_tokens += input_tokens
        dialog.output_tokens += output_tokens
        dialog.save()
        print("dialog filter: ", dialog)
    else:
        dialog = Dialog.objects.create(
            user=user,
            chat_mode=user.current_chat_mode,
            gpt_model=user.current_model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        print("dialog create: ", dialog)
    if Messages_dialog.objects.filter(dialog=dialog, msg_token=random_token, end=False).exists():
        print("message filter: ", random_token,
              Messages_dialog.objects.filter(dialog=dialog, msg_token=random_token, end=False).last())
        msg = Messages_dialog.objects.filter(dialog=dialog, msg_token=random_token, end=False).last()
        msg.user = message
        msg.bot = answer
        msg.input_tokens = input_tokens
        msg.output_tokens = output_tokens
        msg.end = True
        msg.save()
        print("message filter: ", msg)
    else:
        msg = Messages_dialog.objects.create(
            user=message,
            bot=answer,
            dialog=dialog,
            msg_token=uuid.uuid4().hex,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            end=True,
        )
        print("message create: ", msg)
    print("message.msg_token: ", msg.msg_token)
    return msg.msg_token


@sync_to_async
def create_msg_token(user, token):
    if Dialog.objects.filter(user=user, end=False).exists():
        dialog = Dialog.objects.filter(user=user, end=False).last()
        dialog.save()
    else:
        dialog = Dialog.objects.create(
            user=user,
            chat_mode=user.current_chat_mode,
            gpt_model=user.current_model,
        )
    message = Messages_dialog.objects.create(
        dialog=dialog,
        msg_token=token,
    )
    message.save()

    return message.msg_token


@sync_to_async
def check_msg_token(user):
    if Dialog.objects.filter(user=user, end=False).exists():
        dialog = Dialog.objects.filter(user=user, end=False).last()
        dialog.save()
    else:
        dialog = Dialog.objects.create(
            user=user,
            chat_mode=user.current_chat_mode,
            gpt_model=user.current_model,
        )
    if Messages_dialog.objects.filter(dialog=dialog, end=False).exists():
        return False
    return True


@sync_to_async
def generate_prompt(user, message, bot_name):
    message = message.replace(f"@{bot_name}", "")
    print("message: ", message)

    message = message.strip()

    print("message: ", message)
    promt = user.current_chat_mode.prompt_start
    messages_list = [{"role": "system", "content": promt}]
    if Dialog.objects.filter(user=user, end=False).exists():
        dialog = Dialog.objects.filter(user=user, end=False).last()
        print("\n\n\n-dialog: ", dialog)
        # get last 3 messages
        print("messages count: ", Messages_dialog.objects.filter(dialog=dialog, end=True).count())

        if Messages_dialog.objects.filter(dialog=dialog, end=True).count() > 0:
            print("messages count: ", Messages_dialog.objects.filter(dialog=dialog, end=True).count())
            messages = list(Messages_dialog.objects.filter(dialog=dialog, end=True).order_by("-created_at")[:3])
            messages.reverse()

            print("messages: ", messages)
            if messages:
                for msg in messages:
                    messages_list.append({"role": "user", "content": msg.user})
                    messages_list.append({"role": "assistant", "content": msg.bot})
                messages_list.append({"role": "user", "content": message})
                print("messages_list: ", messages_list)
                return messages_list
            else:
                messages_list.append({"role": "user", "content": message})
                print("messages_list: ", messages_list)
                return messages_list
        else:
            messages_list.append({"role": "user", "content": message})
            print("messages_list: ", messages_list)
            return messages_list
    else:
        messages_list.append({"role": "user", "content": message})
        print("messages_list: ", messages_list)
        return messages_list


async def send_message_stream(message, model_name, chat_token, user, update, context, random_token, *args, **kwargs):
    openai_key = await get_openai_key()
    openai.api_key = openai_key

    def _postprocess_answer(answer):
        answer = answer.strip()
        return answer

    await create_msg_token(user, random_token)

    answer = None

    messages = await generate_prompt(user, message, context.bot.username)
    print("messages: ", messages)

    await context.bot.send_chat_action(chat_id=update.message.chat_id, action="typing")
    msg_dot = await context.bot.send_message(chat_id=update.message.chat_id, text="⌛️Loading...",
                                             parse_mode=ParseMode.MARKDOWN,
                                             reply_to_message_id=update.message.message_id)
    msg_message_id = msg_dot.message_id
    msg_chat_id = update.message.chat_id
    print("message_id: ", msg_message_id)
    print("chat_id: ", msg_chat_id)
    try:
        while answer is None:
            print("create time: ", datetime.now())
            r_gen = openai.ChatCompletion.create(
                model=model_name,
                messages=messages,
                stream=True,
                temperature=0.7,
                max_tokens=1000,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                timeout=600,
            )
            answer = ""
            i = 1
            for r_item in r_gen:
                delta = r_item.choices[0].delta
                if "content" in delta:
                    answer += delta.content

            await context.bot.edit_message_text(
                chat_id=update.message.chat_id,
                text=_postprocess_answer(answer),
                message_id=msg_dot.message_id,
                parse_mode=ParseMode.MARKDOWN,
            )
            print("answer: ", answer)
            input_message = messages
            output_message = [{"role": "assistant", "content": answer}]

            input_tokens = await num_tokens_from_messages(input_message, model_name)
            output_tokens = await num_tokens_from_messages(output_message, model_name)

            print("input_tokens: ", input_tokens)
            print("output_tokens: ", output_tokens)
            print("user: ", message)
            print("assistant: ", answer)

            await create_msg(message, answer, user, input_tokens, output_tokens, random_token)

            return answer
    except Exception as e:
        message = (f"ChatGPT bot error:\n"
                   f"Sorry, I'm experiencing some issues. Please try again later.\n"
                   f"\ntoken:\n <b>{openai_key}</b>\n\n"
                   f"gpt token error:\n {e}")
        await send_msg_log(message)
        await msg_dot.delete()
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Sorry, I'm experiencing some issues. Please try again later.",action="typing",
            # parse_mode=ParseMode.MARKDOWN,
        )
        await delete_messages(random_token)

        return None
