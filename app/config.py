import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_API_URL = os.getenv("LLM_API_URL")
    REDIS_URL = os.getenv("REDIS_URL")

settings = Settings()
