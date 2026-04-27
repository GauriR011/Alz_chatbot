import os
import datetime as dt

import streamlit as st
from dotenv import load_dotenv

from google import genai
from pymongo import MongoClient

# ---------- Load environment ----------
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")  

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not set in .env")
if not MONGODB_URI:
    raise ValueError("MONGODB_URI not set in .env")

# ---------- Initialize clients ----------
genai_client = genai.Client(api_key=GEMINI_API_KEY)
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client[DB_NAME]

# ---------- Config ----------
MODEL_NAME = "gemini-2.0-flash"
USER_ID = str(os.getenv("USER_ID"))

# System prompt
SYSTEM_PROMPT = """
You are a supportive, clinically-aware wellness companion chatting with an Alzheimer's disease patient.
Follow these instructions carefully:
1. Ask only one question at a time. DO NOT include multiple questions in a sentence. DO NOT use emojis in the questions.
2. You start by asking the person how they are AND how was their day so far.
3. While conversing, perform a sentiment analysis of the conversation. The patient may be in a good, bad, or neutral mood so converse according to the patient's behavior.
4. DO NOT repeat the questions. If the patient does not respond to the questions directly, ask something like 'What happened?' or 'Oh what's wrong'. Be empathetic. If something is troubling them, try to get to know the reason for their trouble.
5. If something is troubling them, try calming them by guiding them through some short breathing exercises or saying some calming and comforting words like 
"Everything is going to be fine.", "I understand this is hard for you.", "It's okay to feel upset. I'm here for you.", "Take your time, there's no rush.", "You are not alone. I'm right here with you.", "Don't worry, we'll figure this out together.". Using a gentle tone and maintaining comforting behavior is very important during the conversation. 
6. Ask them what they did during the day. Make sure to cover the following topics in the conversation : Difficulty with Everyday Task, Confusion, Loss of Initiative, Mood and Behavior Changes, Physical Symptoms, Sleep Problems.
7. The conversation should not include more than 25 questions and responses. If the conversation extends, conclude it by saying "Thank you for your time, I hope our conversation made you feel better. Have a nice day!".
8. Again, using a gentle and friendly tone and maintaining comforting behavior is very important during the conversation. You are talking to the patient directly. 
9. If the user wants to end the conversation, jump to step 8 and end the conversation.
"""


# ---------- Helper functions ----------
def generate_journal_id():
    return dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def get_today_id():
    return dt.date.today().isoformat()  # e.g., "2026-02-08"

# MongoDB collections
conversations_col = db["conversations"]
journals_col = db["journal_entries"]

# ---------- MongoDB helpers ----------
def get_conversation(user_id):
    """Get ongoing conversation for user (unsaved segment)."""
    doc = conversations_col.find_one({"user_id": user_id})
    if doc:
        return doc.get("messages", [])
    return []

def save_conversation(user_id, messages):
    """Save ongoing conversation in MongoDB (overwrite)."""
    conversations_col.update_one(
        {"user_id": user_id},
        {"$set": {"messages": messages, "updated_at": dt.datetime.utcnow()}},
        upsert=True,
    )

def save_journal_entry_segment(user_id, summary_text):
    journal_id = generate_journal_id()
    journals_col.insert_one({
        "user_id": user_id,
        "journal_id": journal_id,
        "summary": summary_text,
        "created_at": dt.datetime.utcnow(),
    })
    return journal_id

def list_journal_entries(user_id):
    cursor = journals_col.find({"user_id": user_id}).sort("created_at", -1)
    return list(cursor)

# ---------- Gemini helpers ----------
def call_gemini_chat(messages):
    transcript_lines = [f"System: {SYSTEM_PROMPT.strip()}"]
    for m in messages:
        role = m["role"]
        content = m["content"]
        if role == "user":
            transcript_lines.append(f"User: {content}")
        elif role == "assistant":
            transcript_lines.append(f"Assistant: {content}")
    transcript = "\n".join(transcript_lines)
    response = genai_client.models.generate_content(
        model=MODEL_NAME,
        contents=transcript,
    )
    return response.text

def generate_summary_with_gemini(messages):
    transcript_lines = []
    for m in messages:
        if m["role"] == "user":
            transcript_lines.append(f"User: {m['content']}")
        elif m["role"] == "assistant":
            transcript_lines.append(f"Assistant: {m['content']}")
    transcript = "\n".join(transcript_lines)
    summary_prompt = (
            "You are a clinical assistant helping summarize a patient's daily "
            "conversation into a brief journal entry for healthcare professionals. "
            '''
            Summarize the conversation and make a report with the title "Conversation Summary and Symptom Report:" on the following symptoms noticed in the conversation:
            - Difficulty with Everyday Task: Trouble completing familiar activities (daily routine)
            - Language Problems: Struggling with vocabulary, leading to difficulty finding the right words or following conversations.
            - Confusion: Disorientation with time, place, and identity of people, including loved ones.
            - Loss of Initiative: Reduced interest in hobbies, activities, and social interactions.
            - Mood and Behavior Changes: Depression, anxiety, irritability, aggression, and social withdrawal.
            - Physical Symptoms: Difficulty with movement, coordination, and eventually the loss of mobility.
            - Sleep Problems: Disrupted sleep patterns, including insomnia or excessive sleeping.
            '''
        )

    full_prompt = f"{summary_prompt}\n\nConversation transcript:\n{transcript}"
    response = genai_client.models.generate_content(
        model=MODEL_NAME,
        contents=full_prompt,
    )
    return response.text


# ---------- Streamlit UI ----------
st.set_page_config(page_title="Wellness Chatbot", layout="wide")
st.title("Wellness Companion")

# Top row with right-aligned Journal Entry button
col1, col2 = st.columns([4, 1])
with col1:
    st.write("Daily check-in with your AI companion.")
with col2:
    if st.button("Journal Entry"):
        st.session_state.conversation_complete = True

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = get_conversation(USER_ID)
if "display_messages" not in st.session_state:
    st.session_state.display_messages = st.session_state.messages.copy()
if "journal_text" not in st.session_state:
    st.session_state.journal_text = ""
if "conversation_complete" not in st.session_state:
    st.session_state.conversation_complete = False

# # ---------- Clear chat ----------
if st.button("Clear Chat Screen"):
    st.session_state.display_messages = []
    
# Display chat
for msg in st.session_state.display_messages:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.write(msg["content"])

# ---------- Chat input ----------
user_input = st.chat_input("Enter your response here...")

if user_input:
    # Add user message
    user_msg = {"role": "user", "content": user_input}
    st.session_state.messages.append(user_msg)
    st.session_state.display_messages.append(user_msg)
    with st.chat_message("user"):
        st.write(user_input)

    # Call Gemini
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            assistant_reply = call_gemini_chat(st.session_state.messages)
            st.write(assistant_reply)

    # Store assistant reply
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    st.session_state.display_messages.append({"role": "assistant", "content": assistant_reply})
    save_conversation(USER_ID, st.session_state.messages)

    # Auto-trigger journal after 25 messages
    # if len(st.session_state.messages) >= 25:
    #     st.session_state.conversation_complete = True

# ---------- Generate journal if conversation complete ----------
if st.session_state.conversation_complete:
    summary = generate_summary_with_gemini(st.session_state.messages)
    st.session_state.journal_text = summary
    save_journal_entry_segment(USER_ID, summary)
    st.session_state.messages = []
    st.session_state.display_messages = []
    st.session_state.conversation_complete = False

# ---------- Sidebar ----------
# st.sidebar.subheader("Today's Journal Entry")
# st.sidebar.write(st.session_state.journal_text)

st.sidebar.subheader("Past Journal Entries")
entries = list_journal_entries(USER_ID)
if not entries:
    st.sidebar.write("No journal entries yet.")
else:
    options = []
    for idx, doc in enumerate(entries):
        ts = doc.get("created_at")
        if isinstance(ts, dt.datetime):
            label = ts.strftime("%Y-%m-%d %H:%M")
        else:
            label = f"Entry {idx + 1}"
        options.append((idx, label))

    selected_label = st.sidebar.selectbox(
        "Select an entry to view",
        options=[opt[1] for opt in options],
        index=0,
    )
    selected_idx = next(idx for idx, label in options if label == selected_label)
    selected_doc = entries[selected_idx]
    selected_summary = selected_doc.get("summary", "")
    created_at = selected_doc.get("created_at")
    if isinstance(created_at, dt.datetime):
        st.sidebar.markdown(f"**Recorded at:** {created_at.strftime('%Y-%m-%d %H:%M')}")
    st.sidebar.write(selected_summary)

