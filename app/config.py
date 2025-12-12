from pydantic import BaseSettings
from dotenv import load_dotenv
import os

# Load .env file before Settings() is initialized
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

class Settings(BaseSettings):
    MONGO_URI: str
    MONGO_DB: str = "org_master"
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_MINUTES: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
