from llm.gemini_client import client
from config.settings import MODEL_NAME

def generate_summary(messages):
    transcript = "\n".join(
        [f"{m['role']}: {m['content']}" for m in messages]
    )

    prompt = f"""
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

        Conversation:
        {transcript}
    """

    res = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return res.text