from llm.gemini_client import client
from config.settings import EMBED_MODEL

def get_embedding(text):
    res = client.models.embed_content(
        model=EMBED_MODEL,
        contents=text
    )
    return res.embeddings[0].values