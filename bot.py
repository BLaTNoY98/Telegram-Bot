import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask
import config

# Flask app yaratish
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

# Telegram bot sozlash
TOKEN = config.TELEGRAM_TOKEN

# Telegram bot yaratish
application = ApplicationBuilder().token(TOKEN).build()

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Salom! Telegram botga xush kelibsiz.")

# Komanda qo‘shish
application.add_handler(CommandHandler("start", start))

# Botni ishga tushirish
if __name__ == '__main__':
    application.run_polling()  # BU QATORNI FLASKDAN OLDIN ISHLATISH KERAK
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
