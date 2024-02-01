from asgiref.sync import sync_to_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from apps.chatgpt_bot.models import Chat_mode




@sync_to_async
def get_chat_modes_keyboard(page_index: int = 0, items_per_page: int = 5):
    chat_modes = Chat_mode.objects.all()
    total_chat_modes = len(chat_modes)

    start_index = page_index * items_per_page
    end_index = (page_index + 1) * items_per_page

    chat_modes_page = chat_modes[start_index:end_index]

    keyboard = []
    for chat_mode in chat_modes_page:
        keyboard.append([InlineKeyboardButton(chat_mode.model_name, callback_data=f"set_chat_modes_{chat_mode.id}")])

    # Pagination
    if total_chat_modes > items_per_page:
        is_first_page = (page_index == 0)
        is_last_page = (end_index >= total_chat_modes)

        pagination_buttons = []
        if not is_first_page:
            pagination_buttons.append(InlineKeyboardButton("« Previous", callback_data=f"show_chat_modes_{page_index - 1}"))

        if not is_last_page:
            pagination_buttons.append(InlineKeyboardButton("Next »", callback_data=f"show_chat_modes_{page_index + 1}"))

        if pagination_buttons:
            keyboard.append(pagination_buttons)

    return InlineKeyboardMarkup(keyboard)
