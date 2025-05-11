import logging
import os
import sys
import requests




sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from admin import get_handlers as get_admin_handlers
from target import get_targetolog_panel_handlers
from operator_panel import get_operator_panel_handlers

import config
import db

logging.basicConfig(level=logging.INFO)

# DB ni ishga tushuramiz
db.init_db()


# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if db.is_registered(user_id):
        if user_id in config.ADMIN_IDS:
            await update.message.reply_text("Admin paneliga xush kelibsiz.")
        elif db.is_operator(user_id):
            await show_operator_panel(update, context)
        elif db.is_targetolog(user_id):
            await show_targetolog_panel(update, context)
        else:
            await update.message.reply_text("Siz hali tasdiqlanmagansiz.")
        return

    contact_button = KeyboardButton("Telefon raqamni yuborish", request_contact=True)
    keyboard = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text(
        "Botdan foydalanish uchun iltimos, telefon raqamingizni yuboring:",
        reply_markup=keyboard
    )


# Telefon raqamni qabul qilish
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    if contact is None or contact.phone_number is None:
        await update.message.reply_text("Iltimos, telefon raqamingizni yuboring.")
        return

    if contact.user_id != update.effective_user.id:
        await update.message.reply_text("❌ Telefon raqam o‘zingizga tegishli bo‘lishi kerak.")
        return

    user_id = update.effective_user.id
    phone = contact.phone_number

    db.register_user(user_id, phone)

    await update.message.reply_text("Raqamingiz saqlandi.", reply_markup=ReplyKeyboardRemove())

    if db.is_operator(user_id):
        await update.message.reply_text("Operator sifatida ro‘yxatdan o‘tdingiz. Panel yuklanmoqda...")
        await show_operator_panel(update, context)
    elif db.is_targetolog(user_id):
        await update.message.reply_text("Targetolog sifatida ro‘yxatdan o‘tdingiz. Panel yuklanmoqda...")
        await show_targetolog_panel(update, context)
    elif user_id in config.ADMIN_IDS:
        await update.message.reply_text("Admin sifatida ro‘yxatdan o‘tdingiz. Panel yuklanmoqda...")
    else:
        await update.message.reply_text("Raqamingiz saqlandi, ammo hali tasdiqlanmagansiz.")

    # Adminlarga xabar yuborish
    for admin_id in config.ADMIN_IDS:
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve_user:{user_id}"),
                InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_user:{user_id}")
            ]
        ])
        await context.bot.send_message(
            chat_id=admin_id,
            text=f"Yangi foydalanuvchi ro‘yxatdan o‘tdi:\n\nID: {user_id}\nTelefon: {phone}",
            reply_markup=keyboard
        )


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
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("Operator paneliga xush kelibsiz:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text("Operator paneliga xush kelibsiz:", reply_markup=reply_markup)


# Targetolog paneli
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
        await update.callback_query.edit_message_text("Targetolog Paneli:", reply_markup=reply_markup)


# Callback tugmalari ishlovchi funksiya
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    user_id = query.from_user.id

    if data.startswith("approve_user:"):
        new_user_id = int(data.split(":")[1])
        db.approve_user(new_user_id)
        await query.edit_message_text(f"✅ Foydalanuvchi {new_user_id} tasdiqlandi.")
        return

    if data.startswith("reject_user:"):
        new_user_id = int(data.split(":")[1])
        db.reject_user(new_user_id)
        await query.edit_message_text(f"❌ Foydalanuvchi {new_user_id} rad etildi.")
        return

    if db.is_operator(user_id):
        await query.edit_message_text(f"Operator paneli: {data}")
    elif db.is_targetolog(user_id):
        if data == "my_leads":
            await query.edit_message_text("Sizning leadlaringiz hali yo‘q.")
        elif data == "my_balance":
            await query.edit_message_text("Sizning balansingiz: 0 so‘m.")
        elif data == "add_sale":
            await query.edit_message_text("Sotuv qo‘shish funksiyasi hali mavjud emas.")
        else:
            await query.edit_message_text("Noma’lum tugma.")
    elif user_id in config.ADMIN_IDS:
        await query.edit_message_text("Admin panelda tugma bosildi.")
    else:
        await query.edit_message_text("Sizda panelga kirish huquqi yo‘q.")


# Botni ishga tushurish
    if __name__ == "__main__":
    
    application = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    application.add_handler(CallbackQueryHandler(callback_handler))

    application.add_handlers(get_operator_panel_handlers())
    application.add_handlers(get_targetolog_panel_handlers())
    application.add_handlers(get_admin_handlers())

    application.run_polling()
