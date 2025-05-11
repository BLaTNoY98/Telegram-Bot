from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler, ContextTypes
from config import ADMIN_IDS  # admin ID ro'yxati
from db import (get_all_operators, block_operator, unblock_operator,
                get_statistics, get_all_targetologs, block_targetolog,
                unblock_targetolog, get_all_products)

def admin_panel(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        return

    keyboard = [
        [InlineKeyboardButton("📋 Operatorlar", callback_data='admin_operators')],
        [InlineKeyboardButton("🎯 Targetologlar", callback_data='admin_targetologs')],
        [InlineKeyboardButton("📦 Mahsulotlar", callback_data='admin_products')],
        [InlineKeyboardButton("📊 Statistika", callback_data='admin_stats')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Admin paneliga xush kelibsiz!", reply_markup=reply_markup)



# Admin komandasi uchun handler
async def start_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Admin paneliga xush kelibsiz!")

# Handlerlarni qaytaruvchi funksiya
def get_admin_handlers():
    return [
        CommandHandler("admin", start_admin)
    ]
def admin_callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data

    if data == 'admin_operators':
        operators = get_all_operators()
        text = "📋 *Operatorlar ro'yxati:*\n\n"
        keyboard = []
        for op in operators:
            text += f"👤 {op['name']} | ID: {op['id']} | {'❌ Blocklangan' if op['blocked'] else '✅ Aktiv'}\n"
            row = [
                InlineKeyboardButton("❌ Block" if not op['blocked'] else "✅ Unblock",
                                     callback_data=f"blockop_{op['id']}")
            ]
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_back")])
        query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == 'admin_targetologs':
        targets = get_all_targetologs()
        text = "🎯 *Targetologlar ro'yxati:*\n\n"
        keyboard = []
        for tg in targets:
            text += f"👤 {tg['name']} | ID: {tg['id']} | {'❌ Blocklangan' if tg['blocked'] else '✅ Aktiv'}\n"
            row = [
                InlineKeyboardButton("❌ Block" if not tg['blocked'] else "✅ Unblock",
                                     callback_data=f"blocktg_{tg['id']}")
            ]
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_back")])
        query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == 'admin_products':
        products = get_all_products()
        text = "📦 *Mahsulotlar ro'yxati:*\n\n"
        keyboard = []
        for pr in products:
            status = "✅ Aktiv" if pr['enabled'] else "❌ O'chirilgan"
            text += f"🆔 {pr['id']} - {pr['title']} | {status}\n"
        keyboard.append([InlineKeyboardButton("➕ Yangi mahsulot qo‘shish", callback_data="add_product")])
        keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_back")])
        query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == 'admin_stats':
        stats = get_statistics()
        text = (
            f"📊 *Statistika:*\n\n"
            f"🔹 Bugungi leadlar: {stats['daily']}\n"
            f"🔸 Haftalik leadlar: {stats['weekly']}\n"
            f"🔹 Oylik leadlar: {stats['monthly']}\n"
        )
        keyboard = [[InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_back")]]
        query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == 'admin_back':
        admin_panel(update, context)

    elif data.startswith('blockop_'):
        op_id = int(data.split('_')[1])
        # Toggle block
        updated = block_operator(op_id)
        text = "Operator holati o‘zgartirildi."
        query.edit_message_text(text)
        # You can call back the operator list here if needed

    elif data.startswith('blocktg_'):
        tg_id = int(data.split('_')[1])
        # Toggle block
        updated = block_targetolog(tg_id)
        text = "Targetolog holati o‘zgartirildi."
        query.edit_message_text(text)

    elif data == 'add_product':
        query.edit_message_text("➕ Yangi mahsulot qo‘shish uchun /addproduct buyrug‘ini yuboring.")

# Qo‘shish kerak bo‘lgan handlerlar
admin_handlers = [
    CommandHandler("admin", admin_panel),
    CallbackQueryHandler(admin_callback_handler, pattern="^admin_"),
    CallbackQueryHandler(admin_callback_handler, pattern="^(blockop_|blocktg_|add_product)$"),
    ]
