import streamlit as st
import threading

from config.settings import USER_ID
from db.conversations import get_conversation, save_conversation, clear_conversation
from db.journals import save_journal
from llm.chat import call_chat_stream
from llm.summarizer import generate_summary
from rag.indexer import index_new_journals
from ui.chat_screen import render_chat
from ui.sidebar import render_sidebar

st.set_page_config(layout="wide", page_title="Wellness Companion")

# 1. Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = get_conversation(USER_ID)

# 2. Header and "End Chat" Button
# Placing the button at the top keeps the bottom clear for the sticky input
col_title, col_end = st.columns([4, 1])
with col_title:
    st.title("Wellness Companion")
with col_end:
    st.write("##") # Alignment spacing
    end_chat = st.button("End Chat", use_container_width=True, type="primary")

# 3. Sidebar (Journals & RAG)
render_sidebar(USER_ID)

# 4. Render Chat History
# We use a container to ensure the chat stays scrollable above the input
chat_container = st.container()
with chat_container:
    render_chat(st.session_state.messages)

# 5. Chat Input (Root level so it sticks to the bottom)
user_input = st.chat_input("Type your message here...")

# 6. Handle Logic
if end_chat:
    if st.session_state.messages:
        with st.spinner("Summarizing and indexing..."):
            summary = generate_summary(st.session_state.messages)
            save_journal(USER_ID, summary, st.session_state.messages)
            index_new_journals(USER_ID)
            clear_conversation(USER_ID)
            st.session_state.messages = []
        st.success("Journal saved!")
        st.rerun()
    else:
        st.warning("No conversation to save.")

if user_input:
    # Append user message
    user_msg = {"role": "user", "content": user_input}
    st.session_state.messages.append(user_msg)
    
    # Re-render to show user message immediately
    with chat_container:
        with st.chat_message("user"):
            st.write(user_input)

    # Stream Assistant Response
    with chat_container:
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""
            for chunk in call_chat_stream(st.session_state.messages):
                full_response = chunk
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)

    # Update state and background save
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    msg_copy = st.session_state.messages.copy()
    threading.Thread(target=save_conversation, args=(USER_ID, msg_copy)).start()