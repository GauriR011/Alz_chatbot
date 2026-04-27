import streamlit as st

def render_chat(messages):
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

st.markdown('<div id="chat-bottom"></div>', unsafe_allow_html=True)