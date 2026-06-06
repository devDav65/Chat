import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Chatbot Gemini FastAPI"
    PROJECT_VERSION: str = "1.0.0"

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    SECRET_KEY: str = os.getenv("SECRET_KEY")

settings = Settings()