# -----------------Google Translate API-----------------#
from google.cloud import translate
from asgiref.sync import sync_to_async
import logging


logger = logging.getLogger(__name__)

PROJECT_ID = "ubuntu-407908"
assert PROJECT_ID
PARENT = f"projects/{PROJECT_ID}"


@sync_to_async
def translate_text_with_lang(text: str, source_language_code: str,
                             target_language_code: str, ) -> translate.Translation:
    client = translate.TranslationServiceClient()

    response = client.translate_text(
        parent=PARENT,
        contents=[text],
        target_language_code=target_language_code,
        source_language_code=source_language_code,
    )

    return response.translations[0]


@sync_to_async
def translate_text_auto_lang(text: str, target_language_code: str, ) -> translate.Translation:
    client = translate.TranslationServiceClient()

    response = client.translate_text(
        parent=PARENT,
        contents=[text],
        target_language_code=target_language_code,
    )

    return response.translations[0]


@sync_to_async
def detect_language(text: str) -> translate.DetectedLanguage:
    client = translate.TranslationServiceClient()

    response = client.detect_language(parent=PARENT, content=text)

    return response.languages[0]


@sync_to_async
def print_supported_languages(display_language_code: str):
    client = translate.TranslationServiceClient()

    response = client.get_supported_languages(
        parent=PARENT,
        display_language_code=display_language_code,
    )

    languages = response.languages
    print(f" Languages: {len(languages)} ".center(60, "-"))
    for language in languages:
        language_code = language.language_code
        display_name = language.display_name
        print(f"{language_code:10}{display_name}")
