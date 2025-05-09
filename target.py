# target.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
import db
from datetime import datetime, timedelta

def build_target_menu():
    keyboard = [
        [InlineKeyboardButton("Buyurtmalarim", callback_data="my_orders")],
        [InlineKeyboardButton("Balansim", callback_data="my_balance")],
        [InlineKeyboardButton("Statistika", callback_data="my_stats")]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_lead_filter_menu():
    keyboard = [
        [InlineKeyboardButton("Yangi", callback_data="leads_new")],
        [InlineKeyboardButton("Qabul qilindi", callback_data="leads_accepted")],
        [InlineKeyboardButton("Yetkazilmoqda", callback_data="leads_shipping")],
        [InlineKeyboardButton("Yetkazildi", callback_data="leads_delivered")],
        [InlineKeyboardButton("Arxiv", callback_data="leads_archived")],
        [InlineKeyboardButton("Ortga", callback_data="back_to_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def target_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not db.is_targetolog(user_id):
        await update.message.reply_text("Siz ro‘yxatdan o‘tgan targetolog emassiz.")
        return
    await update.message.reply_text("Targetolog paneli:", reply_markup=build_target_menu())

async def handle_target_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    telegram_id = query.from_user.id
    targetolog_id = db.get_targetolog_id(telegram_id)

    if data == "my_orders":
        await query.message.edit_text("Buyurtmalar holatini tanlang:", reply_markup=build_lead_filter_menu())

    elif data.startswith("leads_"):
        status = data.split("_")[1]
        status_map = {
            "new": "new",
            "accepted": "accepted",
            "shipping": "shipping",
            "delivered": "delivered",
            "archived": "archived"
        }
        leads = db.get_leads_by_targetolog_and_status(targetolog_id, status_map[status])
        if not leads:
            await query.message.edit_text("Bu holatda buyurtmalar topilmadi.", reply_markup=build_lead_filter_menu())
            return

        text = "\n\n".join([f"{i+1}. {lead[1]} - {lead[2]}\nManzil: {lead[3]}" for i, lead in enumerate(leads)])
        await query.message.edit_text(f"Buyurtmalar ({status_map[status]}):\n\n{text}", reply_markup=build_lead_filter_menu())

    elif data == "my_balance":
        hold, main = db.get_targetolog_balances(targetolog_id)
        keyboard = [[InlineKeyboardButton("Pul yechish uchun ariza", callback_data="withdraw_request")],
                    [InlineKeyboardButton("Ortga", callback_data="back_to_panel")]]
        text = f"Hold balans: {hold} so‘m\nAsosiy balans: {main} so‘m"
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "withdraw_request":
        db.add_withdrawal_request(targetolog_id)
        await query.message.edit_text("Pul yechish uchun ariza yuborildi.", reply_markup=build_target_menu())

    elif data == "my_stats":
        stats = db.get_targetolog_stats(targetolog_id)
        text = (
            f"Kunlik: {stats['daily']}\n"
            f"Haftalik: {stats['weekly']}\n"
            f"Oylik: {stats['monthly']}"
        )
        keyboard = [[InlineKeyboardButton("Ortga", callback_data="back_to_panel")]]
        await query.message.edit_text(f"Leadlar statistikasi:\n\n{text}", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "back_to_panel":
        await query.message.edit_text("Targetolog paneli:", reply_markup=build_target_menu())

def get_handlers():
    return [
        CommandHandler("start", target_start),
        CallbackQueryHandler(handle_target_buttons, pattern="^(my_orders|leads_.*|my_balance|withdraw_request|my_stats|back_to_panel)$")
    ]
