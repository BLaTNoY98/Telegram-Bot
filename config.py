import os
from dotenv import load_dotenv

# .env faylni yuklaymiz
load_dotenv()

# Bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Adminlar ro'yxati (int ko'rinishida)
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))

# Boshqa sozlamalar bo'lsa, shu yerga qo'shish mumkin
