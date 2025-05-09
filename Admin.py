# admin.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
import db

# Ruxsat berilgan adminlar ro‘yxati
ADMINS = [1471552584]  # Sizga kerak bo‘lsa, bu yerga boshqa admin IDlarni ham qo‘shing

# Bosqichlar
ADD_OPERATOR_NAME, ADD_OPERATOR_ID = range(2)
ADD_TARGETOLOG_NAME, ADD_TARGETOLOG_ID = range(2, 4)

operator_temp_data = {}
targetolog_temp_data = {}

def is_admin(user_id):
    return user_id in ADMINS

async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("Siz admin emassiz.")
        return

    keyboard = [
        [InlineKeyboardButton("Operator qo‘shish", callback_data="add_operator")],
        [InlineKeyboardButton("Targetolog qo‘shish", callback_data="add_targetolog")],
        [InlineKeyboardButton("Operatorlar ro‘yxati", callback_data="list_operators")],
        [InlineKeyboardButton("Targetologlar ro‘yxati", callback_data="list_targetologs")],
        [InlineKeyboardButton("Statistika", callback_data="show_stats")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Admin paneliga xush kelibsiz:", reply_markup=reply_markup)

async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "add_operator":
        await query.message.reply_text("Operator ismini yuboring:")
        return ADD_OPERATOR_NAME

    if data == "add_targetolog":
        await query.message.reply_text("Targetolog ismini yuboring:")
        return ADD_TARGETOLOG_NAME

    if data == "list_operators":
        operators = db.get_all_operators()
        if not operators:
            await query.message.reply_text("Operatorlar topilmadi.")
        else:
            msg = "\n".join([f"{op[0]}: {op[1]} (ID: {op[2]})" for op in operators])
            await query.message.reply_text(f"Operatorlar:\n{msg}")

    if data == "list_targetologs":
        targetologs = db.get_all_targetologs()
        if not targetologs:
            await query.message.reply_text("Targetologlar topilmadi.")
        else:
            msg = "\n".join([f"{tg[0]}: {tg[1]} (ID: {tg[2]})" for tg in targetologs])
            await query.message.reply_text(f"Targetologlar:\n{msg}")

    if data == "show_stats":
        operator_count = db.count_operators()
        targetolog_count = db.count_targetologs()
        lead_count = db.count_leads()
        msg = (
            f"Statistika:\n"
            f"Operatorlar: {operator_count}\n"
            f"Targetologlar: {targetolog_count}\n"
            f"Leadlar: {lead_count}"
        )
        await query.message.reply_text(msg)

    return ConversationHandler.END

# Operator qo‘shish
async def add_operator_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    operator_temp_data["name"] = update.message.text
    await update.message.reply_text("Operator Telegram ID sini yuboring:")
    return ADD_OPERATOR_ID

async def add_operator_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        telegram_id = int(update.message.text)
        name = operator_temp_data["name"]
        db.add_operator(name, telegram_id)
        await update.message.reply_text("Operator qo‘shildi.")
    except Exception as e:
        await update.message.reply_text(f"Xatolik: {e}")
    return ConversationHandler.END

# Targetolog qo‘shish
async def add_targetolog_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    targetolog_temp_data["name"] = update.message.text
    await update.message.reply_text("Targetolog Telegram ID sini yuboring:")
    return ADD_TARGETOLOG_ID

async def add_targetolog_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        telegram_id = int(update.message.text)
        name = targetolog_temp_data["name"]
        db.add_targetolog(name, telegram_id)
        await update.message.reply_text("Targetolog qo‘shildi.")
    except Exception as e:
        await update.message.reply_text(f"Xatolik: {e}")
    return ConversationHandler.END

def get_handlers():
    return [
        CommandHandler("admin", admin_start),
        CallbackQueryHandler(admin_buttons),
        ConversationHandler(
            entry_points=[
                CallbackQueryHandler(admin_buttons, pattern="add_operator|add_targetolog")
            ],
            states={
                ADD_OPERATOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_operator_name)],
                ADD_OPERATOR_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_operator_id)],
                ADD_TARGETOLOG_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_targetolog_name)],
                ADD_TARGETOLOG_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_targetolog_id)],
            },
            fallbacks=[]
        )
    ]
