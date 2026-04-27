from llm.gemini_client import client
from config.settings import MODEL_NAME
from prompts.system_prompt import SYSTEM_PROMPT

# def call_chat(messages):
#     transcript = "System: " + SYSTEM_PROMPT + "\n"

#     for m in messages:
#         role = "User" if m["role"] == "user" else "Assistant"
#         transcript += f"{role}: {m['content']}\n"

#     res = client.models.generate_content(
#         model=MODEL_NAME,
#         contents=transcript
#     )
#     return res.text

# def call_chat_stream(messages):
#     transcript = ...

#     response = client.models.generate_content_stream(
#         model=MODEL_NAME,
#         contents=transcript,
#     )

#     full_text = ""
#     for chunk in response:
#         if chunk.text:
#             full_text += chunk.text
#             yield full_text

def call_chat_stream(messages):
    # Rebuild the transcript so the model knows the history
    transcript = "System: " + SYSTEM_PROMPT + "\n"
    for m in messages:
        role = "User" if m["role"] == "user" else "Assistant"
        transcript += f"{role}: {m['content']}\n"

    response = client.models.generate_content_stream(
        model=MODEL_NAME,
        contents=transcript,
    )

    full_text = ""
    for chunk in response:
        if chunk.text:
            full_text += chunk.text
            yield full_text

            