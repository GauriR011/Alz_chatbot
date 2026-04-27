import numpy as np
from db.journals import get_all_journals
from rag.embedder import get_embedding
import datetime as dt

def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def retrieve(query, user_id, top_k=3):
    query_emb = get_embedding(query)
    journals = get_all_journals(user_id)

    scored = []
    for j in journals:
        if not j.get("embedding"):
            continue
        sim = cosine_sim(query_emb, j["embedding"])
        scored.append((sim, j))

    scored.sort(reverse=True, key=lambda x: x[0])
    return [x[1] for x in scored[:top_k]]


# 🔥 time-aware retrieval
def filter_by_time(journals, days=7):
    cutoff = dt.datetime.utcnow() - dt.timedelta(days=days)
    return [j for j in journals if j["created_at"] >= cutoff]