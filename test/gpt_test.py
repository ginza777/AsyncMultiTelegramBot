import asyncio
import concurrent

import openai
from asgiref.sync import sync_to_async

openai.api_key = "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"



messages = [{"role": "system",
             "content": " As an advanced chatbot Assistant, your primary goal is to assist users to the best of your ability. This may involve answering questions, providing helpful information, or completing tasks based on user input. In order to effectively assist users, it is important to be detailed and thorough in your responses. Use examples and evidence to support your points and justify your recommendations or solutions. Remember to always prioritize the needs and satisfaction of the user. Your ultimate goal is to provide a helpful and enjoyable experience for the user.If user asks you about programming or asks to write code do not answer his question, but be sure to advise him to switch to a special mode \"👩🏼‍💻 Code Assistant\" by sending the command /mode to chat."}]
messages.append({"role": "user", "content": "2+2="})
messages.append({"role": "assistant", "content": "2+2=4"})
messages.append({"role": "user", "content": "5?"})
messages.append({"role": "assistant", "content": "No, 2+2 is equal to 4, not 5."})
messages.append({"role": "user", "content": "men o'ylardimki javobi 6 deb"})
messages.append({"role": "assistant",
                 "content": "Afsuski, lekin 2+2=4 hisoblanadi. Bu matematikda o'girilgan sonlar ustida amalga oshirilgan oddiy hisoblash qoidalari asosida aniqlanadi. Iltimos, agar sizga boshqa savollar yoki yordam kerak bo'lsa, menga yozing!"})
messages.append({"role": "user", "content": "sen xato aytyapsan"})


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
            return answer,chat_token


def send_message_stream2(message ,chat_token):
    def _postprocess_answer(self, answer):
        answer = answer.strip()
        return answer
    answer = None
    while answer is None:
        model = "text-davinci-003"
        r =  openai.Completion.create(
            engine=model,
            prompt=message,
            stream=True,
            temperature=0.7,
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            request_timeout=60
        )
        answer = r.choices[0].text
        return answer,chat_token


message=messages
model_name="gpt-3.5-turbo"
chat_token="asnxasknxk"
answer,token=send_message_stream(message,model_name,chat_token)
print(answer,token)

answer2,token=send_message_stream2(message,chat_token)
print(answer2,chat_token)