#backend/app/core/config.py
from dotenv import load_dotenv
import os
from pathlib import Path

# Load .env explicitly (Windows-safe)
BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

settings = Settings()

