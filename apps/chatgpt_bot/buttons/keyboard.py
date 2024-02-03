from telegram import KeyboardButton, ReplyKeyboardMarkup


def generate_keyboard(items):
    keyboard = []
    row = []

    for item in items:
        row.append(KeyboardButton(str(item)))

        if len(row) == 2:
            keyboard.append(row)
            row = []

    # If there's an odd number of items, add the last one in a new row
    if row:
        keyboard.append(row)

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)