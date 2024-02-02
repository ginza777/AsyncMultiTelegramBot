from django.core.management.base import BaseCommand

from apps.chatgpt_bot.models import Chat_mode, Config, GptModels

from .config_list import assistant_list, config, model_list


def fill_gpt_models():
    for model in model_list:
        GptModels.objects.get_or_create(model=model["key"], config=model)
        print(f"model {model['key']} created successfully.")


def fill_chat_mode():
    for mode in assistant_list:
        Chat_mode.objects.get_or_create(
            key=mode["key"],
            model_name=mode["name"],
            model_type=mode["model_type"],
            welcome_message=mode["welcome_message"],
            prompt_start=mode["prompt_start"],
            parse_mode=mode["parse_mode"],
        )
        print(f"mode {mode['key']} created successfully.")


def fill_config():
    Config.objects.get_or_create(
        openai_api_base=config["openai_api_base"],
        new_dialog_timeout=config["new_dialog_timeout"],
        return_n_generated_images=config["return_n_generated_images"],
        n_chat_modes_per_page=config["n_chat_modes_per_page"],
        image_size=config["image_size"],
        enable_message_streaming=config["enable_message_streaming"],
        chatgpt_price_per_1000_tokens=config["chatgpt_price_per_1000_tokens"],
        gpt_price_per_1000_tokens=config["gpt_price_per_1000_tokens"],
        whisper_price_per_1_min=config["whisper_price_per_1_min"],
    )
    print(f"config created successfully.")


class Command(BaseCommand):
    help = "fill the database with the default values"

    def handle(self, *args, **options):
        fill_gpt_models()
        fill_chat_mode()
        fill_config()
        print("done")
