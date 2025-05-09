from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)
import db

ASK_ADDRESS = range(1)
pending_address = {}

# Yangi leadlar ro‘yxatini ko‘rsatish
async def view_new_leads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    leads = db.get_new_leads_for_operator(query.from_user.id)

    if not leads:
        await query.edit_message_text("Yangi leadlar yo‘q.")
        return

    for lead in leads:
        lead_id, name, phone, address = lead
        msg = f"Ism: {name}\nTelefon: {phone}"
        if address:
            msg += f"\nManzil: {address}"
        keyboard = [
            [InlineKeyboardButton("Qabul qilish", callback_data=f"accept_{lead_id}")],
            [InlineKeyboardButton("Callback", callback_data=f"callback_{lead_id}")],
            [InlineKeyboardButton("Arxivlash", callback_data=f"archive_{lead_id}")]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(msg, reply_markup=markup)

# Qabul qilish
async def accept_lead(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lead_id = int(query.data.split("_")[1])
    lead = db.get_lead_by_id(lead_id)

    if not lead:
        await query.edit_message_text("Lead topilmadi.")
        return ConversationHandler.END

    if not lead[3]:  # address yo‘q
        pending_address[query.from_user.id] = lead_id
        await query.message.reply_text("Iltimos, mijoz manzilini yuboring:")
        return ASK_ADDRESS

    db.accept_lead(lead_id, query.from_user.id)
    await query.edit_message_text("Lead qabul qilindi va hold balansga qo‘shildi.")
    return ConversationHandler.END

# Manzil qabul qilish
async def receive_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    address = update.message.text

    if user_id not in pending_address:
        await update.message.reply_text("Kutilmagan xatolik.")
        return ConversationHandler.END

    lead_id = pending_address.pop(user_id)
    db.update_lead_address(lead_id, address)
    db.accept_lead(lead_id, user_id)

    await update.message.reply_text("Manzil saqlandi. Lead qabul qilindi va hold balansga qo‘shildi.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Callback qilish
async def callback_lead(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lead_id = int(query.data.split("_")[1])
    db.set_lead_status(lead_id, "callback")
    await query.edit_message_text("Lead callback uchun belgilandi.")

# Arxivlash
async def archive_lead(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lead_id = int(query.data.split("_")[1])
    db.set_lead_status(lead_id, "archived")
    await query.edit_message_text("Lead arxivlandi.")

# Balans ko‘rsatish
async def view_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    hold, main = db.get_balances(user_id)
    await query.edit_message_text(f"Hold balans: {hold} so‘m\nAsosiy balans: {main} so‘m")

# Handlerlar ro‘yxatini qaytarish
def get_operator_handlers():
    return [
        CallbackQueryHandler(view_new_leads, pattern="^view_new_leads$"),
        CallbackQueryHandler(accept_lead, pattern="^accept_"),
        CallbackQueryHandler(callback_lead, pattern="^callback_"),
        CallbackQueryHandler(archive_lead, pattern="^archive_"),
        CallbackQueryHandler(view_balance, pattern="^view_balance$"),
        ConversationHandler(
            entry_points=[CallbackQueryHandler(accept_lead, pattern="^accept_")],
            states={
                ASK_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_address)]
            },
            fallbacks=[],
        )
  ]
