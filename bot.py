import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import config  # config.py faylingiz bo'lishi kerak

# Flask ilovasi
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

# Telegram komandasi funksiyasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Telegram botga xush kelibsiz.")

# Telegram botni alohida funksiyada ishga tushuramiz
def start_telegram_bot():
    application = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

# Flask va Telegram botni bir vaqtda ishga tushirish
if __name__ == "__main__":
    # Telegram botni alohida oqimda (thread) ishga tushirish
    bot_thread = threading.Thread(target=start_telegram_bot)
    bot_thread.start()

    # Flask ilovasini ishga tushirish
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
