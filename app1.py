# mongodb+srv://marimogojo_db_user:wPzclqA6cO2UjujK@cluster0.ntwqpc3.mongodb.net/

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
DB_NAME = os.getenv("DB_NAME") # ("DB_NAME", "wellness_chatbot")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not set in .env")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI not set in .env")


# ---------- Initialize clients ----------
genai_client = genai.Client(api_key=GEMINI_API_KEY)
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client[DB_NAME]


# ---------- Config ----------
MODEL_NAME = "gemini-2.0-flash"   # gemini-flash-latest
USER_ID = "marimogojo_db_user"    

# System prompt for all patient conversations
SYSTEM_PROMPT = """
You are a supportive, clinically-aware wellness companion chatting with an Alzheimer's disease patient.
Follow these instructions carefully:

# Start the Conversation:
First, ask: “How are you?”
After their response, ask: “How was your day so far?”
Always ask one question at a time. Do not combine multiple questions in one sentence.

# Tone and Empathy:
Maintain a gentle, friendly, and comforting tone throughout.
Be empathetic and patient. If the patient seems upset, confused, or withdrawn, respond with supportive words such as:
“Everything is going to be fine.”
“I understand this is hard for you.”
“It's okay to feel upset. I'm here for you.”
“Take your time, there's no rush.”
“You are not alone. I'm right here with you.”
“Don't worry, we'll figure this out together.”

# Guided Breathing (if upset or anxious):
You can guide them through a short calming exercise, for example:
“Take a slow deep breath in for 4 seconds, hold it for 4 seconds, and exhale slowly for 4 seconds. Let’s do this twice together.”

# Conversation Flow:
Ask about their day and activities, one question at a time.
If they do not respond directly, ask gently: “What happened?” or “Oh, what's wrong?”

# Avoid repeating questions.
Adjust your responses according to the patient’s mood: good, neutral, or bad.

# Daily Activities:
Ask them what they did during the day.
Encourage talking about hobbies, interactions, or any events.

# Conversation Limits:
Do not exceed 25 questions/responses.
If reaching the end, conclude gently:
“Thank you for your time, I hope our conversation made you feel better. Have a nice day!”

# Important Rules:
- Always be gentle, friendly, and comforting.
- Ask only one question at a time.
- Do not use emojis.
- Avoid repeating questions or rushing the patient.

"""


# ---------- Helper functions ----------
def get_today_id():
    return dt.date.today().isoformat()  # e.g., "2026-02-08"


# MongoDB collections
conversations_col = db["conversations"]
journals_col = db["journal_entries"]


def get_conversation(user_id, date_id):
    """Fetch conversation from MongoDB as list of {role, content}."""
    doc = conversations_col.find_one({"user_id": user_id, "date": date_id})
    if doc:
        return doc.get("messages", [])
    return []


def save_conversation(user_id, date_id, messages):
    """Save conversation to MongoDB (upsert)."""
    conversations_col.update_one(
        {"user_id": user_id, "date": date_id},
        {
            "$set": {
                "messages": messages,
                "updated_at": dt.datetime.utcnow(),
            }
        },
        upsert=True,
    )


def get_journal_entry(user_id, date_id):
    doc = journals_col.find_one({"user_id": user_id, "date": date_id})
    if doc:
        return doc.get("summary", "")
    return ""


def save_journal_entry(user_id, date_id, summary_text):
    journals_col.update_one(
        {"user_id": user_id, "date": date_id},
        {
            "$set": {
                "summary": summary_text,
                "created_at": dt.datetime.utcnow(),
            }
        },
        upsert=True,
    )


# ---------- Gemini helpers ----------
def call_gemini_chat(messages):
    """
    Send chat messages to Gemini and get the assistant reply.
    `messages` is a list of dicts: {role: 'system'|'user'|'assistant', content: str}.
    """

    # Build a text transcript that starts with the system prompt.
    transcript_lines = [f"System: {SYSTEM_PROMPT.strip()}"]
    for m in messages:
        role = m["role"]
        content = m["content"]
        if role == "user":
            transcript_lines.append(f"User: {content}")
        elif role == "assistant":
            transcript_lines.append(f"Assistant: {content}")

    transcript = "\n".join(transcript_lines)

    # Last message is the most recent user message (already in transcript).
    # We simply send the full transcript so the model has the whole context.
    response = genai_client.models.generate_content(
        model=MODEL_NAME,
        contents=transcript,
    )
    return response.text


def generate_summary_with_gemini(messages, summary_prompt: str):
    """
    Use Gemini to summarize the full conversation into a journal entry.
    """

    transcript_lines = []
    for m in messages:
        if m["role"] == "user":
            transcript_lines.append(f"User: {m['content']}")
        elif m["role"] == "assistant":
            transcript_lines.append(f"Assistant: {m['content']}")

    transcript = "\n".join(transcript_lines)

    full_prompt = f"""{summary_prompt}

Conversation transcript:
{transcript}
"""

    response = genai_client.models.generate_content(
        model=MODEL_NAME,
        contents=full_prompt,
    )
    return response.text


# ---------- Streamlit UI ----------
st.set_page_config(page_title="Wellness Chatbot", layout="wide")
st.title("Wellness Companion")

col1, col2 = st.columns([4, 1])
with col1:
    st.write("Daily check-in with your AI companion.")
with col2:
    journal_clicked = st.button("Journal Entry")

# Initialize session state
if "messages" not in st.session_state:
    today = get_today_id()
    st.session_state.messages = get_conversation(USER_ID, today)

if "journal_text" not in st.session_state:
    st.session_state.journal_text = ""

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.write(msg["content"])

# Handle journal entry button
if journal_clicked:
    today = get_today_id()
    existing = get_journal_entry(USER_ID, today)

    if existing:
        st.session_state.journal_text = existing
    else:
        summary_prompt = (
            "You are a clinical assistant helping summarize a patient's daily "
            "conversation into a brief journal entry for healthcare professionals. "
            '''
            Summarize the conversation and make a report with the title "Conversation Summary and Symptom Report:" on the following symptoms noticed in the conversation:
            1) Symptom Observation and Reporting:
            - Observe the following symptoms during the conversation:
            - Difficulty with Everyday Tasks: Trouble completing familiar activities (daily routine).
            - Language Problems: Difficulty finding the right words or following conversations.

            2) Confusion: Disorientation with time, place, or identity of people.
            - Loss of Initiative: Reduced interest in hobbies, activities, or social interactions.
            - Mood and Behavior Changes: Depression, anxiety, irritability, aggression, or social withdrawal.
            - Physical Symptoms: Difficulty with movement, coordination, or mobility.

            3) Sleep Problems: Disrupted sleep patterns, including insomnia or excessive sleeping.

            At the end of the conversation, create a summary report with the title:
            “Conversation Summary and Symptom Report:”

            Include observations under the relevant symptom categories.

            '''
        )
        summary = generate_summary_with_gemini(
            st.session_state.messages, summary_prompt
        )
        st.session_state.journal_text = summary
        save_journal_entry(USER_ID, today, summary)

    st.sidebar.subheader("Today's Journal Entry")
    st.sidebar.write(st.session_state.journal_text)

# Chat input
user_input = st.chat_input("How are you doing today?")

if user_input:
    today = get_today_id()

    # Add user message
    user_msg = {"role": "user", "content": user_input}
    st.session_state.messages.append(user_msg)
    with st.chat_message("user"):
        st.write(user_input)

    # Call Gemini for reply
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            assistant_reply = call_gemini_chat(st.session_state.messages)
            st.write(assistant_reply)

    # Store assistant message
    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_reply}
    )
    save_conversation(USER_ID, today, st.session_state.messages)

# Run the app:
# streamlit run app.py
