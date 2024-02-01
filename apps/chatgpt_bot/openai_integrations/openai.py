import openai
from asgiref.sync import sync_to_async

from apps.chatgpt_bot.openai_integrations.token_calculator import num_tokens_from_messages, _count_tokens_from_prompt


@sync_to_async
def send_message_stream(message, model_name, chat_token, promt):
    openai.api_key = "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"

    def _postprocess_answer(self, answer):
        answer = answer.strip()
        return answer

    answer = None

    messages = [
        {"role": "system", "content": promt},
        {"role": "user", "content": message},
    ]

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

            model = "gpt-3.5-turbo-0613"
            print(f"{num_tokens_from_messages(messages, model)} prompt tokens counted.")
            # Should show ~126 total_tokens
            # count input and output tokens
            # count input tokens
            input_tokens = num_tokens_from_messages(messages, model_name)
            # count output tokens
            output_tokens = num_tokens_from_messages(messages + [{"role": "assistant", "content": answer}], model_name)

            print("input_tokens: ", input_tokens)
            print("output_tokens: ", output_tokens)
            print("user: ",message)
            print("assisant: ",answer)
            return answer, chat_token
