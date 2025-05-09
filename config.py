import os
from dotenv import load_dotenv

load_dotenv()

# Environment Variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int.getenv("ADMIN_ID")
