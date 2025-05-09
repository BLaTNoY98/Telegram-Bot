import logging
from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    KeyboardButton, 
    ReplyKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    CallbackQueryHandler, 
    ContextTypes, 
    MessageHandler, 
    ConversationHandler, 
    filters
)
import config
import db

# Log sozlash
logging.basicConfig(level=logging.INFO)

# Bosqichlar
ADD_OPERATOR_NAME, ADD_OPERATOR_ID = range(2)
operator_temp_data = {}

# DB ni ishga tushirish
db.init_db()

# Panel funksiyasi
async def show_targetolog_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Leadlarim", callback_data="my_leads")],
        [InlineKeyboardButton("Balansim", callback_data="my_balance")],
        [InlineKeyboardButton("Sotuv qo‘shish", callback_data="add_sale")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("Targetolog Paneli:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("Targetolog Paneli:", reply_markup=reply_markup)

# Start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact_button = KeyboardButton("Telefon raqamni yuborish", request_contact=True)
    keyboard = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text(
        "Botdan foydalanish uchun iltimos, telefon raqamingizni yuboring:",
        reply_markup=keyboard
    )

# Kontaktni qabul qilish
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    if contact is None or contact.phone_number is None:
        await update.message.reply_text("Iltimos, telefon raqamingizni yuboring.")
        return

    if contact.user_id != update.effective_user.id:
        await update.message.reply_text("❌ Telefon raqam o‘zingizga tegishli bo‘lishi kerak.")
        return

    is_op = db.is_operator(update.effective_user.id)
if is_op:
    await update.message.reply_text("Operator sifatida ro‘yxatdan o‘tdingiz. Panel yuklanmoqda...")
    await show_operator_panel(update, context)
else:
    await update.message.reply_text("Targetolog sifatida ro‘yxatdan o‘tdingiz. Panel yuklanmoqda...")
    await show_targetolog_panel(update, context)
    await show_targetolog_panel(update, context)

# Callback tugmalar
async def targetolog_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data == "my_leads":
        await query.edit_message_text("Sizning leadlaringiz hali yo‘q.")
    elif data == "my_balance":
        await query.edit_message_text("Sizning balansingiz: 0 so‘m.")
    elif data == "add_sale":
        await query.edit_message_text("Sotuv qo‘shish funksiyasi hali mavjud emas.")
    else:
        await query.edit_message_text("Noma’lum tugma.")

# Admin panel
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != config.ADMIN_ID:
        await update.message.reply_text("Siz admin emassiz.")
        return

    keyboard = [
        [InlineKeyboardButton("Top 5 Targetologlar", callback_data='top5')],
        [InlineKeyboardButton("Operator qo‘shish", callback_data='add_operator')],
        [InlineKeyboardButton("Balanslarni ko‘rish", callback_data='view_balances')],
        [InlineKeyboardButton("Leadlar holati", callback_data='check_leads')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Admin Panel:", reply_markup=reply_markup)

# Top 5 funksiyasi
async def top5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.name, COUNT(s.id) as sales_count
        FROM sales s
        JOIN targetologlar t ON s.targetolog_id = t.id
        GROUP BY s.targetolog_id
        ORDER BY sales_count DESC
        LIMIT 5
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("Hozircha hech qanday sotuvlar yo‘q.")
        return

    text = "**Top 5 Targetologlar (Sotuvlar bo‘yicha):**\n\n"
    for i, (name, count) in enumerate(rows, 1):
        text += f"{i}. {name} – {count} ta sotuv\n"

    await update.message.reply_text(text, parse_mode="Markdown")

# Operator qo‘shish
async def add_operator_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operatorning ismini yuboring:")
    return ADD_OPERATOR_NAME

async def add_operator_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    operator_temp_data['name'] = update.message.text
    await update.message.reply_text("Endi operatorning Telegram ID raqamini yuboring:")
    return ADD_OPERATOR_ID

async def add_operator_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        telegram_id = int(update.message.text)
        name = operator_temp_data['name']

        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO operators (telegram_id, name) VALUES (?, ?)", (telegram_id, name))
        conn.commit()
        conn.close()

        await update.message.reply_text(f"✅ Operator '{name}' muvaffaqiyatli qo‘shildi!")
    except ValueError:
        await update.message.reply_text("❌ Noto‘g‘ri ID. Faqat raqam yuboring.")
    return ConversationHandler.END

# Bekor qilish
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bekor qilindi.")
    return ConversationHandler.END

# Application yaratish va ishga tushirish
if __name__ == "__main__":
    application = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CommandHandler("top5", top5))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    application.add_handler(CallbackQueryHandler(targetolog_callback))

    add_operator_conv = ConversationHandler(
        entry_points=[CommandHandler('add_operator', add_operator_start)],
        states={
            ADD_OPERATOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_operator_name)],
            ADD_OPERATOR_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_operator_id)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(add_operator_conv)

    application.run_polling()
