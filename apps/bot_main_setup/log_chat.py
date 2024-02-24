import datetime

import requests
from asgiref.sync import sync_to_async

from apps.chatgpt_bot.models import LogSenderBot


def send_to_telegram(bot_token, chat_id, filename, caption):
    caption += f"\nDate: {datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    files = {'document': open(f"{filename}", 'rb')}
    data = {'chat_id': chat_id, 'caption': caption} if caption else {'chat_id': chat_id}
    response = requests.post(url, files=files, data=data)
    return response.json()




@sync_to_async()
def send_msg_log(message):
    # Define maximum length for each message chunk
    max_length = 4096

    if LogSenderBot.objects.all().count() > 0:
        token = LogSenderBot.objects.last().token
    else:
        token = "6567332198:AAHRaGT5xLJdsJbWkugqgSJHbPGi8Zr2_ZI"
    chat_id = -1002120483646

    # Split the message into chunks
    message_chunks = [message[i:i+max_length] for i in range(0, len(message), max_length)]


    for chunk in message_chunks:
        # Format the chunk as code (HTML-style markdown)
        formatted_chunk = f"<code>{chunk}</code>"

        url = f'https://api.telegram.org/bot{token}/sendMessage'
        params = {
            'chat_id': chat_id,
            'text': formatted_chunk,
            'parse_mode': 'HTML'
        }
        r = requests.post(url, data=params)
        print("r: ", r.status_code)
        print("r: ", r.text)
        if r.status_code != 200:
            return False

    return True


def send_msg(message):
    print("send_msg: ", message)
    if LogSenderBot.objects.all().count() > 0:
        token = LogSenderBot.objects.last().token
        chat_id = LogSenderBot.objects.last().channel_id
    else:
        token = "6567332198:AAHRaGT5xLJdsJbWkugqgSJHbPGi8Zr2_ZI"
        chat_id = -1002120483646

    url = f'https://api.telegram.org/bot{token}/sendMessage'
    params = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        r = requests.post(url, data=params)
    except Exception as e:
        print(e)
    print("r: ", r.status_code)
    if r.status_code == 200:
        return True
    else:
        return False


def send_as_photo(image_caption, image, token, channel_id):
    url = f'https://api.telegram.org/bot{token}/sendPhoto'
    params = {
        'chat_id': channel_id,
        'caption': image_caption,
        'parse_mode': 'HTML',
        'photo': image,
    }
    r = requests.post(url, data=params)
    if r.status_code != 200:
        return False, r.status_code
    else:
        return True, r.status_code
