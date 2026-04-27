import datetime as dt
from db.mongo import db

col = db["journal_entries"]

def save_journal(user_id, summary, raw_messages):
    doc = {
        "user_id": user_id,
        "summary": summary,
        "raw_messages": raw_messages,
        "created_at": dt.datetime.utcnow(),
        "embedded": False,
        "embedding": None
    }
    col.insert_one(doc)

def get_all_journals(user_id):
    return list(col.find({"user_id": user_id}).sort("created_at", -1))

def get_unembedded_journals(user_id):
    return list(col.find({"user_id": user_id, "embedded": False}))

def update_embedding(doc_id, embedding):
    col.update_one(
        {"_id": doc_id},
        {"$set": {"embedding": embedding, "embedded": True}}
    )