from rag.retriever import retrieve, filter_by_time
from llm.gemini_client import client
from config.settings import MODEL_NAME

def rag_answer(query, user_id):
    journals = retrieve(query, user_id)

    # detect "past week"
    if "week" in query.lower():
        journals = filter_by_time(journals, 7)

    context = "\n\n".join([
        f"Date: {j['created_at']}\nSummary: {j['summary']}"
        for j in journals
    ])

    prompt = f"""
You are an expert clinical data assistant. Your task is to accurately answer questions regarding a patient's symptom history and daily journals.

Patient History Context:
{context}

Question:
{query}

Strict Instructions:
1. Grounding: You must base your answer STRICTLY on the "Patient History Context" provided above.
2. No Hallucinations: If the provided context does not contain the information needed to answer the question, you must explicitly state: "There is no information regarding this in the provided patient history." Do not guess or infer medical conditions outside the text.
3. Clarity: If synthesizing information across multiple days, use bullet points and explicitly reference the relevant dates.
4. Tone: Maintain a professional, objective, and clinically aware tone.
"""

    res = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return res.text