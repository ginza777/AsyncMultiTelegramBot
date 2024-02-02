import openai

openai.api_key = "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"


async def send_message_stream(message, model_name):
    async def _postprocess_answer(self, answer):
        answer = answer.strip()
        return answer

    print("send_message_stream")
    answer = None
    while answer is None:
        print("while")
        try:
            print("try:")
            if model_name in {"gpt-3.5-turbo-16k", "gpt-3.5-turbo", "gpt-4", "gpt-4-1106-preview"}:
                print("if")
                messages = message
                print(message)
                r_gen = await openai.ChatCompletion.create(
                    model=model_name,
                    messages=messages,
                    stream=True,
                    temperature=0.7,
                    max_tokens=1000,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    request_timeout=60,
                )
                print("r-gen:  ", r_gen)
                answer = ""
            #     async for r_item in r_gen:
            #         delta = r_item.choices[0].delta
            #         if "content" in delta:
            #             answer += delta.content
            #             # n_input_tokens, n_output_tokens = self._count_tokens_from_messages(messages, answer, model=model_name)
            #             yield "not_finished", answer
            #
            # answer =await _postprocess_answer(answer)
            # print(answer)

        except openai.error.InvalidRequestError as e:
            raise e

    yield "finished", answer
    # n_input_tokens, n_output_tokens), n_first_dialog_messages_removed  # sending final answer


# Example usage:


import asyncio


async def main():
    async for status, response in send_message_stream("salom", "gpt-3.5-turbo"):
        if status == "finished":
            print("Final response:", response)


# Run the event loop
asyncio.run(main())
