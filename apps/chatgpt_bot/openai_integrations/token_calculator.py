import json

import tiktoken
from asgiref.sync import sync_to_async


def _count_tokens_from_prompt(prompt, answer, model="text-davinci-003"):
    encoding = tiktoken.encoding_for_model(model)
    prompt_str = json.dumps(prompt)  # Convert the prompt to a JSON string
    n_input_tokens = len(encoding.encode(prompt_str)) + 1
    n_output_tokens = len(encoding.encode(answer))
    return n_input_tokens, n_output_tokens


@sync_to_async
def num_tokens_from_messages(messages, model):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    num_tokens = 0
    for message in messages:
        num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":  # if there's a name, the role is omitted
                num_tokens += -1  # role is always required and always 1 token

    return num_tokens
