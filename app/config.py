# app/config.py
from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

class Settings(BaseSettings):
    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    JWT_SECRET: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
