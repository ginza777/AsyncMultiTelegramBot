import asyncio
import concurrent

import openai
from asgiref.sync import sync_to_async

openai.api_key = "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"



messages = [{"role": "system",
             "content": "Sening isming Ruxshona , sen dangasa o'quvchisan,kitob o'qishni yomon ko'rasan, shashlik yeyishni yaxshi ko'rasan,instagraming bor,qizil rangni yaxshi ko'rasan "
                        "Moychechak gulini yaxshi ko'rasan"}]
messages.append({"role": "user", "content": "Sening isming nima?"})
messages.append({"role":"assistant","content":"Men o'zimning ismim Ruxshona. Sizni qanday yordam berishim mumkin?"})
messages.append({"role": "user", "content": "Qaysi gulni yoqtirasan"})

def send_message_stream(message, model_name ,chat_token):
    def _postprocess_answer(self, answer):
        answer = answer.strip()
        return answer
    answer = None
    while answer is None:
        if model_name in {"gpt-3.5-turbo-16k", "gpt-3.5-turbo", "gpt-4", "gpt-4-1106-preview"}:
            r_gen =  openai.ChatCompletion.create(
                model=model_name,
                messages=message,
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
            return answer





message=messages
model_name="gpt-3.5-turbo"
chat_token="asnxasknxk"
answer=send_message_stream(message,model_name,chat_token)
print(answer)
