# Wellness Companion

## Overview

A web-based application designed to support individuals with Alzheimer’s disease through daily conversational interaction. The system engages patients in natural dialogue to understand their mood, daily activities, and overall well-being.

The conversations are processed using a Large Language Model (LLM), which extracts meaningful insights and automatically generates structured journal entries. These journals help caregivers and medical professionals monitor cognitive and emotional patterns over time.

In addition, the app includes a **Retrieval-Augmented Generation (RAG)** system that enables healthcare professionals to query patient history and journal logs, making it easier to analyze long-term behavioral and medical trends.



## Target Audience
- **Alzheimer’s Patients:** Helps monitor overall well-being.  
- **Caregivers & Healthcare Professionals:** Provides insights into the patient’s cognitive state and daily activities through automatically generated reports and memory logs.



## Key Features

### Conversational AI Assistant
- Natural language interaction with patients
- Emotion and sentiment-aware responses
- Guided conversation flow to capture daily activities and cognitive indicators

### Automated Journal Generation
- Converts conversations into structured medical-style summaries
- Extracts key insights such as mood, confusion levels, memory issues, and routine adherence

### RAG-Based Medical Query System
- Enables doctors to query patient history using natural language
- Retrieves relevant journal entries from database
- Generates contextualized, evidence-based responses using LLM + retrieved data


## Tech Stack

- **Frontend:** Streamlit   
- **Backend Logic:** Python, MongoDB Atlas    
- **Embeddings:** Google Gemini Embedding API   
- **LLM:** Gemini Flash   

## How It Works

### 1. Patient Conversation
The user interacts with a chatbot powered by an LLM, which guides the conversation to extract relevant daily health and cognitive information.

### 2. Insight Extraction
The LLM processes the conversation to identify:
- Mood and emotional state
- Memory lapses or confusion
- Daily routine adherence
- Behavioral anomalies

### 3. Journal Generation
A structured summary is created and stored in MongoDB as a journal entry.

### 4. RAG System for Doctors
- Journal entries are embedded into a vector space
- Doctor queries are converted into embeddings
- Relevant patient history is retrieved
- LLM generates a contextual response using retrieved data



##  Project Structure

alz_chatbot/      
├── app.py       
├── config/       
│   └── settings.py       
├── prompts/        
│   └── system_prompt.py       
├── db/   
│   ├── mongo.py    
│   ├── conversations.py    
│   └── journals.py   
├── llm/    
│   ├── gemini_client.py    
│   ├── chat.py   
│   └── summarizer.py   
├── rag/    
│   ├── embedder.py   
│   ├── indexer.py    
│   ├── retriever.py    
│   └── rag_chat.py   
├── ui/   
│   ├── chat_screen.py    
│   └── sidebar.py    



**A glimpse of how the project works:**

<img width="3199" height="1722" alt="Chat_screen" src="https://github.com/user-attachments/assets/df8f8594-c800-4478-8b43-e4e3b63cded6" />


https://github.com/user-attachments/assets/7b554151-9b65-4fcd-b45c-168c849c5e33



## Instructions to run the Project:

1) Install dependencies
```{bash}
pip install -r requirements.txt
```

2) Add an API key
Create a .env file under the research copilot folder (main project folder) and add the following line:
```{txt}
GEMINI_API_KEY=you_api_key_here
MONGODB_URI=mongo_db_uri
USER_ID=username
DB_NAME="alz_app_db"
```

3) Run the app
```{bash}
streamlit run app.py
```

*This application was developed with care to support Alzheimer’s patients, their caregivers, and healthcare providers through innovative use of AI and mobile technology.*
