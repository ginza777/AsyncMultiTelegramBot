from telegram import ReplyKeyboardMarkup, KeyboardButton

def generate_keyboard(items):
    keyboard=[]
    row = []
    count = 0

    for item in items:
        count += 1
        row.append(KeyboardButton(str(item)))

        if count % 2 == 0:
            keyboard.append(row)
            row = []

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)