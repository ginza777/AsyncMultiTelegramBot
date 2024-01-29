from apps.chatgpt.models import Chat_mode,Config,GptModels
# config parameters
if Config.objects.count()>0:
    config=Config.objects.last()
else:
    config=Config.objects.create(
    openai_api_base = 'null'
    ).save()
openai_api_base = (config.openai_api_base, None)
new_dialog_timeout = config.new_dialog_timeout
enable_message_streaming = config.enable_message_streaming, True
return_n_generated_images = config.return_n_generated_images, 1
image_size = config.image_size, "512x512"
n_chat_modes_per_page = config.n_chat_modes_per_page, 5


OPENAI_COMPLETION_OPTIONS = {
    "temperature": 0.7,
    "max_tokens": 1000,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "request_timeout": 60.0,
}
