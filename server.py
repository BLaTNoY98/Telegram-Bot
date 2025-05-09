from flask import Flask, request, jsonify
import db
from telegram import Bot

app = Flask(__name__)
bot = Bot(token=config.TELEGRAM_TOKEN)

@app.route('/webhook/lead', methods=['POST'])
def receive_lead():
    data = request.json

    # Kerakli ma'lumotlarni olish
    operator_id = data.get("operator_id")  # Make.com dan keladi
    name = data.get("name")
    phone = data.get("phone")
    address = data.get("address", "")

    # Leadni DB ga qo‘shish
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO leads (operator_id, name, phone, address, status)
        VALUES (?, ?, ?, ?, ?)
    """, (operator_id, name, phone, address, "new"))
    conn.commit()
    conn.close()

    # Operatorga xabar yuborish
    keyboard = [
        [InlineKeyboardButton("Qabul qilish", callback_data=f"accept:{phone}")],
        [InlineKeyboardButton("Callback", callback_data=f"callback:{phone}")],
        [InlineKeyboardButton("Arxivlash", callback_data=f"archive:{phone}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.send_message(
        chat_id=operator_id,
        text=f"Yangi lead:\nIsmi: {name}\nTelefon: {phone}\nManzil: {address or 'yo‘q'}",
        reply_markup=reply_markup
    )

    return jsonify({"status": "ok"})
