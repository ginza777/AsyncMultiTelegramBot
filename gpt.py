from openai import AsyncOpenAI
import asyncio


from openai import OpenAI
import asyncio

class ChatGPTClient:
    def __init__(self, api_key):
        self.client = AsyncOpenAI(api_key=api_key)
        self.user_sessions = {}

    async def get_user_session(self, user_id):
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {"messages": []}
        return self.user_sessions[user_id]

    async def update_user_session(self, user_id, message):
        user_session = await self.get_user_session(user_id)
        user_session["messages"].append({"role": "user", "content": message})

    async def get_assistant_response(self, user_id, message):
        await self.update_user_session(user_id, message)
        user_session = await self.get_user_session(user_id)

        completion = await self.client.chat.completions.create(
            #old session

            user= user_id,
            model="gpt-3.5-turbo-16k-0613",
            messages=user_session["messages"]
        )
        response = completion.choices[0].message.content
        await self.update_user_session(user_id, response)

        print(completion.id)
        print(completion)
        return response

# Example usage:
async def main():
    api_key = "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"
    chat_gpt = ChatGPTClient(api_key)

    user_id_1 = "unique_user_id_1"
    response_1 = await chat_gpt.get_assistant_response(user_id_1, "endi turk tilidachi?")
    print(response_1)
#what is my name?
    # User 2
    user_id_2 = "unique_user_id_2"
    response_2 = await chat_gpt.get_assistant_response(user_id_2, "rus tilidachi?")
    print(response_2)

    # user_id_2 = "unique_user_id_2"
    # response_3 = await chat_gpt.get_assistant_response(user_id_2, "turk tilidachi?")
    # print(response_3)
    # #
    # user_id_2 = "unique_user_id_2"
    # response_4 = await chat_gpt.get_assistant_response(user_id_2, "Xitoy tilidachi?")
    # print(response_4)

# Create an event loop
loop = asyncio.get_event_loop()

# Run the main coroutine
loop.run_until_complete(main())




# async def ChatGPTclient(chat_text):
#     client = AsyncOpenAI(api_key="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")
#     completion = await client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": chat_text}])
#     return completion.choices[0].message.content
#
# # Example usage
# async def main():
#     result = await ChatGPTclient("xitoychadachi?")
#     for token in result.split():
#         print(token, end=' ', flush=True)
#         await asyncio.sleep(0.1)  # Adjust the sleep duration as needed
#
# # Create an event loop
# loop = asyncio.get_event_loop()
#
# # Run the main coroutine
# loop.run_until_complete(main())
