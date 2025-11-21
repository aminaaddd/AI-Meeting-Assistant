import os
from dotenv import load_dotenv
load_dotenv()

MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")

# ✅ Always use French
TARGET_LANG = "fr"

if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY is not set in environment variables.")
