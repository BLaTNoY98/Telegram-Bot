import os 
import logging 
from telegram import (
    Update, 
    InlineKeyboardButton, 
    KeyboardButton,
    InlineKeyboardMarkup,  
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

logging.basicConfig(level=logging.INFO)

db.init_db()

# Bosqichlar

ADD_OPERATOR_NAME, ADD_OPERATOR_ID = range(2)

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): user = update.effective_user

contact_button = KeyboardButton("Telefon raqamni yuborish", request_contact=True)
keyboard = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True, one_time_keyboard=True)

await update.message.reply_text(
    "Botdan foydalanish uchun iltimos, telefon raqamingizni yuboring:",
    reply_markup=keyboard
)

# Kontaktni qabul qilish

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE): contact = update.message.contact user = update.effective_user

if contact and contact.user_id == user.id:
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO targetologlar (name, telegram_id) VALUES (?, ?)",
        (user.full_name, user.id)
    )
    conn.commit()
    conn.close()

    await update.message.reply_text("✅ Ro‘yxatdan o‘tdingiz.")
    await show_targetolog_panel(update, context)
else:
    await update.message.reply_text("❌ Telefon raqam o‘zingizga tegishli bo‘lishi kerak.")

return ConversationHandler.END

# Callback tugmalar

async def targetolog_callback(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query data = query.data await query.answer()

if data == "my_leads":
    await query.edit_message_text("Sizning leadlaringiz hali yo‘q.")
elif data == "my_balance":
    await query.edit_message_text("Sizning balansingiz: 0 so‘m.")
elif data == "add_sale":
    await query.edit_message_text("Sotuv qo‘shish funksiyasi hali mavjud emas.")
else:
    await query.edit_message_text("Noma’lum tugma.")

# Admin panel

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE): if update.effective_user.id != config.ADMIN_ID: await update.message.reply_text("Siz admin emassiz.") return

keyboard = [
    [InlineKeyboardButton("Top 5 Targetologlar", callback_data='top5')],
    [InlineKeyboardButton("Operator qo‘shish", callback_data='add_operator')],
    [InlineKeyboardButton("Balanslarni ko‘rish", callback_data='view_balances')],
    [InlineKeyboardButton("Leadlar holati", callback_data='check_leads')],
]
reply_markup = InlineKeyboardMarkup(keyboard)
await update.message.reply_text("Admin Panel:", reply_markup=reply_markup)

# Top5 komandasi

async def top5(update: Update, context: ContextTypes.DEFAULT_TYPE): conn = db.connect() cursor = conn.cursor() cursor.execute(""" SELECT t.name, COUNT(s.id) as sales_count FROM sales s JOIN targetologlar t ON s.targetolog_id = t.id GROUP BY s.targetolog_id ORDER BY sales_count DESC LIMIT 5 """) rows = cursor.fetchall() conn.close()

if not rows:
    await update.message.reply_text("Hozircha hech qanday sotuvlar yo‘q.")
    return

text = "**Top 5 Targetologlar (Sotuvlar bo‘yicha):**\n\n"
for i, (name, count) in enumerate(rows, 1):
    text += f"{i}. {name} – {count} ta sotuv\n"

await update.message.reply_text(text, parse_mode="Markdown")

# Operator qo‘shish

operator_temp_data = {}

async def add_operator_start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("Operatorning ismini yuboring:") return ADD_OPERATOR_NAME

async def add_operator_name(update: Update, context: ContextTypes.DEFAULT_TYPE): operator_temp_data['name'] = update.message.text await update.message.reply_text("Endi operatorning Telegram ID raqamini yuboring:") return ADD_OPERATOR_ID

async def add_operator_id(update: Update, context: ContextTypes.DEFAULT_TYPE): try: telegram_id = int(update.message.text) name = operator_temp_data['name']

conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO operators (telegram_id, name) VALUES (?, ?)", (telegram_id, name))
    conn.commit()
    conn.close()

    await update.message.reply_text(f"✅ Operator '{name}' muvaffaqiyatli qo‘shildi!")
except ValueError:
    await update.message.reply_text("❌ Noto‘g‘ri ID. Faqat raqam yuboring.")
return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("Bekor qilindi.") return ConversationHandler.END

# Application sozlash

application = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()

application.add_handler(CommandHandler("start", start)) application.add_handler(CommandHandler("admin", admin_panel)) application.add_handler(CommandHandler("top5", top5)) application.add_handler(MessageHandler(filters.CONTACT, handle_contact)) application.add_handler(CallbackQueryHandler(targetolog_callback))

add_operator_conv = ConversationHandler( entry_points=[CommandHandler('add_operator', add_operator_start)], states={ ADD_OPERATOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_operator_name)], ADD_OPERATOR_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_operator_id)], }, fallbacks=[CommandHandler('cancel', cancel)] ) application.add_handler(add_operator_conv)

# Botni ishga tushuramiz

if name == 'main': application.run_polling()

