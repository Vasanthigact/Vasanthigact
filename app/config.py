import os

from dotenv import load_dotenv

load_dotenv()

# Gemini configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

# Application security configuration
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "PocketSmartAI_Secret_Key_2026"
)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Application configuration
APP_NAME = "PocketSmart AI"
APP_VERSION = "1.0.0"