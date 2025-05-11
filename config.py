import os
from dotenv import load_dotenv

# .env faylni yuklaymiz


# Bot token
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Adminlar ro'yxati (int ko'rinishida)
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))

# Boshqa sozlamalar bo'lsa, shu yerga qo'shish mumkin
