import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY = os.getenv("REDACTED_GEMINI_API_KEY")
    PINECONE_API_KEY = os.getenv("ypcsk_4qN96x_8AwoSgYtKDL7EXyoAZ66C3Vhj6iS4H7HoenciM7Mnb2Rj5R4AW7nnFWSpfHCfjB")
    PINECONE_ENVIRONMENT = os.getenv("us-east-1-aws")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    PORT = int(os.getenv("PORT", 8000))

settings = Settings()