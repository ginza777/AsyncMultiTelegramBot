import openai
from asgiref.sync import sync_to_async

@sync_to_async
def send_message_stream(message, model_name, chat_token, promt):
    openai.api_key = "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"

    def _postprocess_answer(self, answer):
        answer = answer.strip()
        return answer

    answer = None

    messages = [{"role": "system", "content": promt}]
    messages.append({"role": "user", "content": message})

    while answer is None:
        if model_name in {"gpt-3.5-turbo-16k", "gpt-3.5-turbo", "gpt-4", "gpt-4-1106-preview"}:
            r_gen = openai.ChatCompletion.create(
                model=model_name,
                messages=messages,
                stream=True,
                temperature=0.7,
                max_tokens=1000,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                request_timeout=60
            )
            answer = ""
            for r_item in r_gen:
                delta = r_item.choices[0].delta
                if "content" in delta:
                    answer += delta.content
            return answer, chat_token