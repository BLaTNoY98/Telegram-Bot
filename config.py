import os
from dotenv import load_dotenv


DB_NAME = "data.db"  # Bu yerga haqiqiy bazangizning nomini yozing

# Bot token
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Adminlar ro'yxati (int ko'rinishida)
ADMIN_IDS = [int(i) for i in os.getenv("ADMIN_IDS", "").split(",") if i.strip().isdigit()]
# Boshqa sozlamalar bo'lsa, shu yerga qo'shish mumkin
