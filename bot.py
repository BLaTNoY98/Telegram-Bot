import logging
import os
import sys

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
import db
from admin import get_handlers as get_admin_handlers
from target import get_targetolog_panel_handlers
from operator_panel import get_operator_panel_handlers

logging.basicConfig(level=logging.INFO)

# DB boshlash
db.init_db()

# Xatoliklar uchun
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error(msg="Exception while handling update:", exc_info=context.error)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("Xatolik yuz berdi. Iltimos, keyinroq urinib ko‘ring.")

# Operator paneli
async def show_operator_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Yangi Leadlar", callback_data="view_new_leads")],
        [InlineKeyboardButton("Qabul Qilingan", callback_data="view_accepted_leads")],
        [InlineKeyboardButton("Yetkazilmoqda", callback_data="view_delivering_leads")],
        [InlineKeyboardButton("Yetkazildi", callback_data="view_delivered_leads")],
        [InlineKeyboardButton("Qaytib Keldi", callback_data="view_returned_leads")],
        [InlineKeyboardButton("Balans", callback_data="view_balance")]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("Operator paneliga xush kelibsiz:", reply_markup=markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text("Operator paneli:", reply_markup=markup)

# Targetolog paneli
async def show_targetolog_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Leadlarim", callback_data="my_leads")],
        [InlineKeyboardButton("Balansim", callback_data="my_balance")],
        [InlineKeyboardButton("Sotuv qo‘shish", callback_data="add_sale")]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("Targetolog paneliga xush kelibsiz:", reply_markup=markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text("Targetolog paneli:", reply_markup=markup)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not db.is_registered(user_id):
        contact_btn = KeyboardButton("Telefon raqamni yuborish", request_contact=True)
        markup = ReplyKeyboardMarkup([[contact_btn]], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            "Iltimos, botdan foydalanish uchun telefon raqamingizni yuboring:",
            reply_markup=markup
        )
        return

    if user_id in config.ADMIN_IDS:
        await update.message.reply_text("Admin paneliga xush kelibsiz.")
    elif db.is_operator(user_id):
        await show_operator_panel(update, context)
    elif db.is_targetolog(user_id):
        await show_targetolog_panel(update, context)
    else:
        await update.message.reply_text("Siz hali tasdiqlanmagansiz.")

# Telefon raqamni qabul qilish
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    user_id = update.effective_user.id
    phone = contact.phone_number

    if contact.user_id != user_id:
        await update.message.reply_text("Faqat o‘z telefon raqamingizni yuboring.")
        return

    db.register_user(user_id, phone)
    await update.message.reply_text("Raqamingiz saqlandi.", reply_markup=ReplyKeyboardRemove())

    if db.is_operator(user_id):
        await update.message.reply_text("Operator sifatida panel yuklanmoqda...")
        await show_operator_panel(update, context)
    elif db.is_targetolog(user_id):
        await update.message.reply_text("Targetolog sifatida panel yuklanmoqda...")
        await show_targetolog_panel(update, context)
    elif user_id in config.ADMIN_IDS:
        await update.message.reply_text("Admin sifatida ro‘yxatdan o‘tdingiz.")
    else:
        await update.message.reply_text("Sizning rolingiz aniqlanmagan, adminlar tasdiqlashi kerak.")

    for admin_id in config.ADMIN_IDS:
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve_user:{user_id}"),
                InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_user:{user_id}")
            ]
        ])
        await context.bot.send_message(
            chat_id=admin_id,
            text=f"Yangi foydalanuvchi:\nID: {user_id}\nTelefon: {phone}",
            reply_markup=keyboard
        )

# Callback tugmalari
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    await query.answer()

    if data.startswith("approve_user:"):
        uid = int(data.split(":")[1])
        db.approve_user(uid)
        await query.edit_message_text(f"✅ Foydalanuvchi {uid} tasdiqlandi.")
        return

    if data.startswith("reject_user:"):
        uid = int(data.split(":")[1])
        db.reject_user(uid)
        await query.edit_message_text(f"❌ Foydalanuvchi {uid} rad etildi.")
        return

    if db.is_operator(user_id):
        await query.edit_message_text(f"Operator paneli: {data}")
    elif db.is_targetolog(user_id):
        await query.edit_message_text("Targetolog funksiyasi: ishlamoqda.")
    elif user_id in config.ADMIN_IDS:
        await query.edit_message_text("Admin funksiyasi: tugma bosildi.")
    else:
        await query.edit_message_text("Sizga bu funksiyalar mavjud emas.")

# Botni ishga tushurish
if __name__ == "__main__":
    app = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_error_handler(error_handler)

    # Qo‘shimcha modullar
    for handler in get_operator_panel_handlers():
        app.add_handler(handler)

    for handler in get_targetolog_panel_handlers():
        app.add_handler(handler)

    for handler in get_admin_handlers():
        app.add_handler(handler)

    app.run_polling()
