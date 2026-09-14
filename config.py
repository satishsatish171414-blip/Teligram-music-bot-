import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION_NAME = os.getenv("SESSION_NAME", "music_user")

if not BOT_TOKEN or not API_ID or not API_HASH:
    raise RuntimeError("Set BOT_TOKEN, API_ID and API_HASH in .env")
