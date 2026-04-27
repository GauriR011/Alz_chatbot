import datetime as dt
from db.mongo import db

col = db["conversations"]

def get_conversation(user_id):
    doc = col.find_one({"user_id": user_id})
    return doc.get("messages", []) if doc else []

def save_conversation(user_id, messages):
    col.update_one(
        {"user_id": user_id},
        {"$set": {"messages": messages, "updated_at": dt.datetime.utcnow()}},
        upsert=True,
    )

def clear_conversation(user_id):
    col.delete_one({"user_id": user_id})