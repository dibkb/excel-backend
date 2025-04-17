from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
load_dotenv()

class Settings(BaseSettings):
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

    POSTGRES_URL: str = os.getenv("POSTGRES_URL")

    SERP_API_KEY: str = os.getenv("SERP_API_KEY")
    BRAVE_SEARCH_API_KEY: str = os.getenv("BRAVE_SEARCH_API_KEY")

    BACKEND_URL: str = os.getenv("BACKEND_URL")


    
    class Config:
        env_file = "../.env"

settings = Settings()