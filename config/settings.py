import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")
USER_ID = os.getenv("USER_ID")

MODEL_NAME = "gemini-flash-latest"
EMBED_MODEL = "gemini-embedding-001"  