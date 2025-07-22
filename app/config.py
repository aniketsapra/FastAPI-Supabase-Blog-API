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
    SUPABASE_PROJECT_ID: str
    SUPABASE_JWKS_URL: str
    SUPABASE_AUDIENCE: str
    SUPABASE_ALGORITHM: str
    SUPABASE_JWT_SECRET: str  

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()


