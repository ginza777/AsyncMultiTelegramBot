from telegram import InlineKeyboardButton, InlineKeyboardMarkup

language_list = [
    {"id": "en", "name": "🏴󠁧󠁢󠁥󠁮󠁧󠁿English"},
    {"id": "ru", "name": "🇷🇺Russian"},
    {"id": "uz", "name": "🇺🇿Uzbek"},
    {"id": "ar", "name": "🇸🇦Arabic"},
    {"id": "az", "name": "🇦🇿Azerbaijani"},
    {"id": "zh", "name": "🇨🇳Chinese (Simplified)"},
    {"id": "zh-CN", "name": "🇨🇳Chinese (Simplified)"},
    {"id": "zh-TW", "name": "🇨🇳Chinese (Traditional)"},
    {"id": "fr", "name": "🇫🇷French"},
    {"id": "de", "name": "🇩🇪German"},
    {"id": "el", "name": "🇬🇷Greek"},
    {"id": "hi", "name": "🇮🇳Hindi"},
    {"id": "it", "name": "🇮🇹Italian"},
    {"id": "ja", "name": "🇯🇵Japanese"},
    {"id": "kk", "name": "🇰🇿Kazakh"},
    {"id": "ky", "name": "🇰🇬Kyrgyz"},
    {"id": "la", "name": "🇻🇦Latin"},
    {"id": "tg", "name": "🇹🇯Tajik"},
    {"id": "tr", "name": "🇹🇷Turkish"},
    {"id": "tk", "name": "🇹🇲Turkmen"},

]


# ar        Arabic
# az        Azerbaijani
# zh        Chinese (Simplified)
# zh-CN     Chinese (Simplified)
# zh-TW     Chinese (Traditional)
# en        English
# fr        French
# de        German
# el        Greek
# hi        Hindi
# it        Italian
# ja        Japanese
# kk        Kazakh
# ky        Kyrgyz
# la        Latin
# ru        Russian
# tg        Tajik
# tr        Turkish
# tk        Turkmen
# uz        Uzbek


def language_list_keyboard(type: str):
    # type = "target"
    # type = "native"
    # reset_native
    # reset_target
    button_list = [
        {"id": "en", "name": "🏴English"},
        {"id": "ru", "name": "🇷🇺Russian"},
        {"id": "uz", "name": "🇺🇿Uzbek"},
        {"id": "ar", "name": "🇸🇦Arabic"},
        {"id": "az", "name": "🇦🇿Azerbaijani"},
        {"id": "zh", "name": "🇨🇳Chinese (Simplified)"},
        {"id": "zh-CN", "name": "🇨🇳Chinese (Simplified)"},
        {"id": "zh-TW", "name": "🇨🇳Chinese (Traditional)"},
        {"id": "fr", "name": "🇫🇷French"},
        {"id": "de", "name": "🇩🇪German"},
        {"id": "el", "name": "🇬🇷Greek"},
        {"id": "hi", "name": "🇮🇳Hindi"},
        {"id": "it", "name": "🇮🇹Italian"},
        {"id": "ja", "name": "🇯🇵Japanese"},
        {"id": "kk", "name": "🇰🇿Kazakh"},
        {"id": "ky", "name": "🇰🇬Kyrgyz"},
        {"id": "la", "name": "🇻🇦Latin"},
        {"id": "tg", "name": "🇹🇯Tajik"},
        {"id": "tr", "name": "🇹🇷Turkish"},
        {"id": "tk", "name": "🇹🇲Turkmen"},
    ]

    sorted_button_list = sorted(button_list, key=lambda x: x["name"])

    print(sorted_button_list)

    keyboard = []
    row = []
    for index, button in enumerate(button_list):
        row.append(InlineKeyboardButton(button['name'], callback_data=f"language_{type}_{button['id']}"))
        if (index + 1) % 2 == 0:  # Append buttons every 2 elements
            keyboard.append(row)
            row = []  # Reset the row

    # Check if there's a leftover button
    if row:
        keyboard.append(row)
    if type == "target":
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f"setting_back_to_native_lang")])

    return InlineKeyboardMarkup(keyboard)


def back_settings():
    keyboard = []
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f"setting_back")])
    return InlineKeyboardMarkup(keyboard)


def inline_lang_generator(lang1, lang2):
    lang1_name = next((item["name"] for item in language_list if item["id"] == lang1), None)
    lang2_name = next((item["name"] for item in language_list if item["id"] == lang2), None)

    keyboard = [
        [
            InlineKeyboardButton(f"Change {lang1_name}", callback_data=f"change_lang_native"),
            InlineKeyboardButton(f"Change {lang2_name}", callback_data=f"change_lang_target")
        ]
    ]

    return InlineKeyboardMarkup(keyboard)
