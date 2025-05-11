import os
import requests
from dotenv import load_dotenv

load_dotenv()  # .env fayldan o'zgaruvchilarni o'qish

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not BOT_TOKEN:
    print("❌ TOKEN topilmadi. Iltimos, .env faylga TELEGRAM_TOKEN qo‘shing.")
    exit()

url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
response = requests.get(url)
print("Webhook delete response:", response.json())
