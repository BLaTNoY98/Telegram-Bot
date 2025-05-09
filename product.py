from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import ADMINS, bot
from db import connect

# Mahsulotlar menyusi
async def product_panel(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("➕ Mahsulot qo‘shish", callback_data="add_product"))
    markup.add(InlineKeyboardButton("📋 Mahsulotlar ro‘yxati", callback_data="list_products"))
    await message.answer("Mahsulotlar paneliga xush kelibsiz!", reply_markup=markup)

# Add product flow
add_product_data = {}

async def start_add_product(call: types.CallbackQuery):
    await call.message.answer("Mahsulot nomini kiriting:")
    add_product_data[call.from_user.id] = {}
    await bot.set_state(call.from_user.id, "product_name")

async def set_product_name(message: types.Message):
    add_product_data[message.from_user.id]["title"] = message.text
    await message.answer("Mahsulot haqida matn kiriting:")
    await bot.set_state(message.from_user.id, "product_description")

async def set_product_description(message: types.Message):
    add_product_data[message.from_user.id]["description"] = message.text
    await message.answer("Mahsulot videosini yuboring (yoki o'tkazib yuboring):")
    await bot.set_state(message.from_user.id, "product_video")

async def set_product_video(message: types.Message):
    if message.video:
        file_id = message.video.file_id
    else:
        file_id = None
    add_product_data[message.from_user.id]["video"] = file_id
    await message.answer("Targetolog uchun narxni kiriting (masalan: 5000):")
    await bot.set_state(message.from_user.id, "price_targetolog")

async def set_price_targetolog(message: types.Message):
    try:
        add_product_data[message.from_user.id]["price_targetolog"] = float(message.text)
    except ValueError:
        return await message.answer("To'g'ri raqam kiriting.")
    await message.answer("Operator uchun narxni kiriting:")
    await bot.set_state(message.from_user.id, "price_operator")

async def set_price_operator(message: types.Message):
    try:
        add_product_data[message.from_user.id]["price_operator"] = float(message.text)
    except ValueError:
        return await message.answer("To'g'ri raqam kiriting.")

    data = add_product_data.pop(message.from_user.id)
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (title, description, video_file_id, price_targetolog, price_operator, is_enabled)
        VALUES (?, ?, ?, ?, ?, 1)
    """, (data["title"], data["description"], data["video"], data["price_targetolog"], data["price_operator"]))
    conn.commit()
    conn.close()
    await message.answer("✅ Mahsulot muvaffaqiyatli qo‘shildi.")

# Mahsulotlar ro'yxati
async def list_products(call: types.CallbackQuery):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, is_enabled FROM products")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return await call.message.answer("Mahsulotlar mavjud emas.")

    for row in rows:
        id, title, is_enabled = row
        status = "✅ Yoqilgan" if is_enabled else "❌ O‘chirilgan"
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✏️ Narxlarni o‘zgartirish", callback_data=f"edit_price:{id}"),
            InlineKeyboardButton("🔁 Holatni almashtirish", callback_data=f"toggle_product:{id}")
        )
        await call.message.answer(f"<b>{title}</b>\nStatus: {status}", reply_markup=markup, parse_mode="HTML")

# Narxlarni o‘zgartirish
price_edit = {}

async def edit_price_start(call: types.CallbackQuery):
    product_id = int(call.data.split(":")[1])
    price_edit[call.from_user.id] = product_id
    await call.message.answer("Yangi Targetolog narxini kiriting:")
    await bot.set_state(call.from_user.id, "edit_price_targetolog")

async def edit_price_targetolog(message: types.Message):
    try:
        target_price = float(message.text)
    except ValueError:
        return await message.answer("To‘g‘ri raqam kiriting.")
    await message.answer("Yangi Operator narxini kiriting:")
    await bot.set_state(message.from_user.id, "edit_price_operator")
    price_edit[message.from_user.id] = {"target_price": target_price, "product_id": price_edit[message.from_user.id]}

async def edit_price_operator(message: types.Message):
    try:
        operator_price = float(message.text)
    except ValueError:
        return await message.answer("To‘g‘ri raqam kiriting.")
    info = price_edit.pop(message.from_user.id)
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products SET price_targetolog = ?, price_operator = ? WHERE id = ?
    """, (info["target_price"], operator_price, info["product_id"]))
    conn.commit()
    conn.close()
    await message.answer("✅ Narxlar yangilandi.")
    # Xabar yuborish
    await notify_price_change(info["product_id"], info["target_price"], operator_price)

# Holatni almashtirish
async def toggle_product_status(call: types.CallbackQuery):
    product_id = int(call.data.split(":")[1])
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT is_enabled FROM products WHERE id = ?", (product_id,))
    current = cursor.fetchone()[0]
    new_status = 0 if current else 1
    cursor.execute("UPDATE products SET is_enabled = ? WHERE id = ?", (new_status, product_id))
    conn.commit()
    conn.close()
    await call.message.answer("Holat yangilandi.")

# Hamma foydalanuvchilarga habar yuborish
async def notify_price_change(product_id, new_target, new_operator):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id FROM targetologlar WHERE is_blocked = 0")
    targetologlar = cursor.fetchall()
    cursor.execute("SELECT telegram_id FROM operators WHERE is_blocked = 0")
    operatorlar = cursor.fetchall()
    cursor.execute("SELECT title FROM products WHERE id = ?", (product_id,))
    title = cursor.fetchone()[0]
    conn.close()

    text = f"⚠️ {title} mahsulot narxlari yangilandi!\n\n" \
           f"Targetolog uchun: {new_target}\nOperator uchun: {new_operator}"

    for row in targetologlar + operatorlar:
        try:
            await bot.send_message(row[0], text)
        except:
            continue

def register_product_handlers(dp: Dispatcher):
    dp.register_message_handler(product_panel, commands=["products"], state="*")

    dp.register_callback_query_handler(start_add_product, text="add_product")
    dp.register_callback_query_handler(list_products, text="list_products")
    dp.register_callback_query_handler(edit_price_start, lambda c: c.data.startswith("edit_price:"))
    dp.register_callback_query_handler(toggle_product_status, lambda c: c.data.startswith("toggle_product:"))

    dp.register_message_handler(set_product_name, state="product_name")
    dp.register_message_handler(set_product_description, state="product_description")
    dp.register_message_handler(set_product_video, content_types=["video", "text"], state="product_video")
    dp.register_message_handler(set_price_targetolog, state="price_targetolog")
    dp.register_message_handler(set_price_operator, state="price_operator")
    dp.register_message_handler(edit_price_targetolog, state="edit_price_targetolog")
    dp.register_message_handler(edit_price_operator, state="edit_price_operator")
