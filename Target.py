from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler
import db

# Targetolog paneli menyusi
async def show_targetolog_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Buyurtmalarim", callback_data="my_orders")],
        [InlineKeyboardButton("Balansim", callback_data="my_balance")],
        [InlineKeyboardButton("Statistika", callback_data="my_stats")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Targetolog paneliga xush kelibsiz:", reply_markup=reply_markup)

# Buyurtmalarim bo‘limi
async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Yangi", callback_data="orders_new")],
        [InlineKeyboardButton("Qabul qilindi", callback_data="orders_accepted")],
        [InlineKeyboardButton("Yetkazilmoqda", callback_data="orders_delivering")],
        [InlineKeyboardButton("Yetkazildi", callback_data="orders_delivered")],
        [InlineKeyboardButton("Arxivlandi", callback_data="orders_archived")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Buyurtmalaringizni status bo‘yicha tanlang:", reply_markup=reply_markup)

async def list_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    status = query.data.replace("orders_", "")
    user_id = query.from_user.id

    orders = db.get_targetolog_leads_by_status(user_id, status)
    if not orders:
        await query.edit_message_text("Bu bo‘limda buyurtmalar topilmadi.")
        return

    text = f"{status.upper()} holatidagi buyurtmalaringiz:\n\n"
    for lead in orders:
        text += f"Ism: {lead['name']}\nTelefon: {lead['phone']}\nManzil: {lead.get('address', '-')}\n\n"
    
    await query.edit_message_text(text)

# Balans bo‘limi
async def my_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    hold_balance = db.get_hold_balance(user_id)
    main_balance = db.get_main_balance(user_id)

    keyboard = [[InlineKeyboardButton("Pul yechish arizasi", callback_data="withdraw_request")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        f"Balansingiz:\n\n"
        f"Hold balans: {hold_balance} so‘m\n"
        f"Asosiy balans: {main_balance} so‘m"
    )
    await query.edit_message_text(text, reply_markup=reply_markup)

async def withdraw_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    db.create_withdrawal_request(user_id)  # Bu funktsiyani db.py faylingizda yozishingiz kerak
    await query.edit_message_text("Pul yechish arizangiz qabul qilindi. Tez orada ko‘rib chiqiladi.")

# Statistika
async def my_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    daily = db.get_daily_stats(user_id)
    weekly = db.get_weekly_stats(user_id)
    monthly = db.get_monthly_stats(user_id)

    text = (
        "Sotuv statistikasi:\n\n"
        f"Kunlik: {daily} ta\n"
        f"Haftalik: {weekly} ta\n"
        f"Oylik: {monthly} ta"
    )
    await query.edit_message_text(text)

# Callback handlerlarni ro‘yxatga olish
def get_targetolog_handlers():
    return [
        CallbackQueryHandler(my_orders, pattern="^my_orders$"),
        CallbackQueryHandler(list_orders, pattern="^orders_"),
        CallbackQueryHandler(my_balance, pattern="^my_balance$"),
        CallbackQueryHandler(withdraw_request, pattern="^withdraw_request$"),
        CallbackQueryHandler(my_stats, pattern="^my_stats$")
    ]
