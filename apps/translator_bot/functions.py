from asgiref.sync import sync_to_async
from apps.translator_bot.models import TranslatorUser, TranslatorConversation


@sync_to_async
def set_lang(translator_user, lang, native: bool):
    print(100*'$')
    print(translator_user, lang, native)
    print(translator_user.native_language, translator_user.target_language)
    if translator_user:
        print("Translator User exists")
        if native:
            print("Native Language")
            translator_user.native_language = lang
            translator_user.save()
            print(translator_user.native_language, translator_user.target_language)
            return True
        if not native:
            translator_user.target_language = lang
            translator_user.save()

            return True
    else:
        return None



@sync_to_async
def save_conversation(user, text, translated_text, source_lang, target_lang):
        TranslatorConversation.objects.create(
            user=user,
            text=text,
            translated_text=translated_text,
            source_language=source_lang,
            target_language=target_lang
        )
