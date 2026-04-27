import streamlit as st
from db.journals import get_all_journals
from rag.rag_chat import rag_answer

def render_sidebar(user_id):
    tab1, tab2 = st.sidebar.tabs(["Journal Entries", "RAG Chatbot"])

    # JOURNALS
    with tab1:
        entries = get_all_journals(user_id)

        for e in entries:
            st.markdown(f"**{e['created_at']}**")
            st.write(e["summary"])
            st.divider()

    # RAG CHAT
    with tab2:
        query = st.text_input("Ask about patient history")

        if query:
            response = rag_answer(query, user_id)
            st.write(response)