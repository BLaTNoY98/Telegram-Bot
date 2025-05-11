from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, filters
)
import db

ADMINS = [1471552584]  # Sizning admin ID'ingiz

# Bosqichlar
ADD_OPERATOR_NAME, ADD_OPERATOR_ID = range(2)
ADD_TARGETOLOG_NAME, ADD_TARGETOLOG_ID = range(2, 4)
ADD_PRODUCT_TITLE, ADD_PRODUCT_DESC, ADD_PRODUCT_VIDEO, ADD_PRODUCT_PRICE_OP, ADD_PRODUCT_PRICE_TG = range(4, 9)
ADD_ADMIN_ID = 9

operator_temp_data = {}
targetolog_temp_data = {}
product_temp_data = {}

def is_admin(user_id):
    return user_id in ADMINS

# /admin komandasi
async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("Siz admin emassiz.")
        return

    keyboard = [
        [InlineKeyboardButton("➕ Operator qo‘shish", callback_data="add_operator")],
        [InlineKeyboardButton("➕ Targetolog qo‘shish", callback_data="add_targetolog")],
        [InlineKeyboardButton("📋 Operatorlar ro‘yxati", callback_data="list_operators")],
        [InlineKeyboardButton("📋 Targetologlar ro‘yxati", callback_data="list_targetologs")],
        [InlineKeyboardButton("📈 Statistika", callback_data="show_stats")],
        [InlineKeyboardButton("🛒 Mahsulot qo‘shish", callback_data="add_product")],
        [InlineKeyboardButton("💰 Balanslar", callback_data="balances")],
        [InlineKeyboardButton("📤 Pul chiqarish so‘rovlari", callback_data="withdrawals")],
        [InlineKeyboardButton("👤 Admin qo‘shish", callback_data="add_admin")],
    ]
    await update.message.reply_text("Admin paneliga xush kelibsiz:", reply_markup=InlineKeyboardMarkup(keyboard))

# Callback tugmalar
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
        msg = "\n".join([f"{op[0]}: {op[1]} (ID: {op[2]})" for op in operators]) if operators else "Operatorlar topilmadi."
        await query.message.reply_text(msg)
        return ConversationHandler.END

    if data == "list_targetologs":
        targetologs = db.get_all_targetologs()
        msg = "\n".join([f"{tg[0]}: {tg[1]} (ID: {tg[2]})" for tg in targetologs]) if targetologs else "Targetologlar topilmadi."
        await query.message.reply_text(msg)
        return ConversationHandler.END

    if data == "show_stats":
        msg = (
            f"📊 Statistika:\n"
            f"👷 Operatorlar: {db.count_operators()}\n"
            f"🎯 Targetologlar: {db.count_targetologs()}\n"
            f"📥 Leadlar: {db.count_leads()}"
        )
        await query.message.reply_text(msg)
        return ConversationHandler.END

    if data == "add_product":
        await query.message.reply_text("Mahsulot nomini yuboring:")
        return ADD_PRODUCT_TITLE

    if data == "balances":
        msg = db.get_balances_summary()
        await query.message.reply_text(msg)
        return ConversationHandler.END

    if data == "withdrawals":
        msg = db.get_pending_withdrawals()
        await query.message.reply_text(msg)
        return ConversationHandler.END

    if data == "add_admin":
        await query.message.reply_text("Yangi adminning Telegram ID sini yuboring:")
        return ADD_ADMIN_ID

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
        await update.message.reply_text("✅ Operator qo‘shildi.")
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
        await update.message.reply_text("✅ Targetolog qo‘shildi.")
    except Exception as e:
        await update.message.reply_text(f"Xatolik: {e}")
    return ConversationHandler.END

# Mahsulot qo‘shish
async def add_product_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_temp_data["title"] = update.message.text
    await update.message.reply_text("Mahsulot tavsifini yuboring:")
    return ADD_PRODUCT_DESC

async def add_product_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_temp_data["description"] = update.message.text
    await update.message.reply_text("Video linkini yuboring:")
    return ADD_PRODUCT_VIDEO

async def add_product_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_temp_data["video_url"] = update.message.text
    await update.message.reply_text("Operator uchun narxni yuboring:")
    return ADD_PRODUCT_PRICE_OP

async def add_product_price_op(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        product_temp_data["price_operator"] = float(update.message.text)
        await update.message.reply_text("Targetolog uchun narxni yuboring:")
        return ADD_PRODUCT_PRICE_TG
    except ValueError:
        await update.message.reply_text("Iltimos, son kiriting.")
        return ADD_PRODUCT_PRICE_OP

async def add_product_price_tg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        product_temp_data["price_targetolog"] = float(update.message.text)
        db.add_product(
            product_temp_data["title"],
            product_temp_data["description"],
            product_temp_data["video_url"],
            product_temp_data["price_operator"],
            product_temp_data["price_targetolog"]
        )
        await update.message.reply_text("✅ Mahsulot qo‘shildi.")
    except Exception as e:
        await update.message.reply_text(f"Xatolik: {e}")
    return ConversationHandler.END

# Yangi admin qo‘shish
async def add_admin_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        new_admin_id = int(update.message.text)
        if new_admin_id not in ADMINS:
            ADMINS.append(new_admin_id)
            await update.message.reply_text("✅ Yangi admin qo‘shildi.")
        else:
            await update.message.reply_text("Bu foydalanuvchi allaqachon admin.")
    except ValueError:
        await update.message.reply_text("ID raqami noto‘g‘ri.")
    return ConversationHandler.END

# Handlerlar
def get_handlers():
    return [
        CommandHandler("admin", admin_start),
        ConversationHandler(
            entry_points=[
                CallbackQueryHandler(admin_buttons, pattern="add_operator|add_targetolog|list_operators|list_targetologs|show_stats|add_product|balances|withdrawals|add_admin")
            ],
            states={
                ADD_OPERATOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_operator_name)],
                ADD_OPERATOR_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_operator_id)],
                ADD_TARGETOLOG_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_targetolog_name)],
                ADD_TARGETOLOG_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_targetolog_id)],
                ADD_PRODUCT_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_title)],
                ADD_PRODUCT_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_desc)],
                ADD_PRODUCT_VIDEO: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_video)],
                ADD_PRODUCT_PRICE_OP: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_price_op)],
                ADD_PRODUCT_PRICE_TG: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_price_tg)],
                ADD_ADMIN_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_admin_id)],
            },
            fallbacks=[],
            per_message=True
        )
    ]
