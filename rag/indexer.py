from db.journals import get_unembedded_journals, update_embedding
from rag.embedder import get_embedding

def index_new_journals(user_id):
    journals = get_unembedded_journals(user_id)

    for j in journals:
        emb = get_embedding(j["summary"])  # embedding summary only
        update_embedding(j["_id"], emb)