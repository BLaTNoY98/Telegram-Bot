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

Log sozlash

logging.basicConfig(level=logging.INFO)

Bosqichlar

ADD_OPERATOR_NAME, ADD_OPERATOR_ID = range(2) operator_temp_data = {}

DB ni ishga tushirish

db.init_db()

Telefon raqam so'ralgan foydalanuvchilarni saqlovchi to'plam

registered_users = set()

Start komandasi

aSync def start(update: Update, context: ContextTypes.DEFAULT_TYPE): user_id = update.effective_user.id

if user_id in registered_users or db.is_registered(user_id):
    if db.is_operator(user_id):
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

Kontaktni qabul qilish

aSync def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE): contact = update.message.contact if contact is None or contact.phone_number is None: await update.message.reply_text("Iltimos, telefon raqamingizni yuboring.") return

if contact.user_id != update.effective_user.id:
    await update.message.reply_text("❌ Telefon raqam o‘zingizga tegishli bo‘lishi kerak.")
    return

user_id = update.effective_user.id
db.register_user(user_id, contact.phone_number)
registered_users.add(user_id)

if db.is_operator(user_id):
    await update.message.reply_text("Operator sifatida ro‘yxatdan o‘tdingiz. Panel yuklanmoqda...")
    await show_operator_panel(update, context)
else:
    await update.message.reply_text("Targetolog sifatida ro‘yxatdan o‘tdingiz. Panel yuklanmoqda...")
    await show_targetolog_panel(update, context)

Panel funksiyalari

aSync def show_operator_panel(update: Update, context: ContextTypes.DEFAULT_TYPE): keyboard = [ [InlineKeyboardButton("Yangi Leadlar", callback_data="view_new_leads")], [InlineKeyboardButton("Qabul Qilingan", callback_data="view_accepted_leads")], [InlineKeyboardButton("Yetkazilmoqda", callback_data="view_delivering_leads")], [InlineKeyboardButton("Yetkazildi", callback_data="view_delivered_leads")], [InlineKeyboardButton("Qaytib Keldi", callback_data="view_returned_leads")], [InlineKeyboardButton("Balans", callback_data="view_balance")], ] reply_markup = InlineKeyboardMarkup(keyboard) await update.message.reply_text("Operator paneliga xush kelibsiz:", reply_markup=reply_markup)

aSync def show_targetolog_panel(update: Update, context: ContextTypes.DEFAULT_TYPE): keyboard = [ [InlineKeyboardButton("Leadlarim", callback_data="my_leads")], [InlineKeyboardButton("Balansim", callback_data="my_balance")], [InlineKeyboardButton("Sotuv qo‘shish", callback_data="add_sale")] ] reply_markup = InlineKeyboardMarkup(keyboard)

await update.message.reply_text("Targetolog Paneli:", reply_markup=reply_markup)

Callback tugmalar

aSync def targetolog_callback(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query data = query.data await query.answer()

if data == "my_leads":
    await query.edit_message_text("Sizning leadlaringiz hali yo‘q.")
elif data == "my_balance":
    await query.edit_message_text("Sizning balansingiz: 0 so‘m.")
elif data == "add_sale":
    await query.edit_message_text("Sotuv qo‘shish funksiyasi hali mavjud emas.")
else:
    await query.edit_message_text("Noma’lum tugma.")

Admin panel va boshqalar shu yerda davom ettiriladi...

if name == "main": application = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
application.add_handler(CallbackQueryHandler(targetolog_callback))

application.run_polling()

