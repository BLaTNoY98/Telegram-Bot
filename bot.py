import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import config
import db  # db.py faylini import qilamiz
ADD_OPERATOR_NAME, ADD_OPERATOR_ID = range(2
TOKEN = config.TELEGRAM_TOKEN
application = ApplicationBuilder().token(TOKEN).build()

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.init_db()
    await update.message.reply_text("Bot ishga tushdi!")

# /top5 komandasi
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

# Komandalarni qo‘shamiz
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("top5", top5))
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# /admin komandasi
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

application.add_handler(CommandHandler("admin", admin_panel))
operator_temp_data = {}

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

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bekor qilindi.")
    return ConversationHandler.END
add_operator_conv = ConversationHandler(
    entry_points=[CommandHandler('add_operator', add_operator_start)],
    states={
        ADD_OPERATOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_operator_name)],
        ADD_OPERATOR_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_operator_id)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
application.add_handler(add_operator_conv)
from telegram.ext import CallbackQueryHandler

# Tugma bosilganda ishlovchi funksiya
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data == 'top5':
        await top5(update, context)
    elif data == 'add_operator':
        await query.edit_message_text("Operator qo‘shish funksiyasi hali tayyor emas.")
    elif data == 'view_balances':
        await query.edit_message_text("Balanslarni ko‘rish funksiyasi hali tayyor emas.")
    elif data == 'check_leads':
        await query.edit_message_text("Lead monitoring funksiyasi hali qo‘shilmagan.")
    else:
        await query.edit_message_text("Noma’lum amal.")
# Botni ishga tushuramiz
if __name__ == '__main__':
    application.run_polling()
    
