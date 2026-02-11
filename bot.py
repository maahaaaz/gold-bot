import os
import json
import asyncio
import aiohttp
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
PORT = int(os.environ.get("PORT", 10000))

DATA_FILE = "data.json"
PRICE_THRESHOLD = 50000  # اختلاف قیمت برای هشدار فوری

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()
app = Flask(__name__)

# ================= وب سرور برای Render =================
@app.route("/")
def home():
    return "Bot is alive!"

def run_web():
    app.run(host="0.0.0.0", port=PORT)

# ================= مدیریت فایل =================
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"interval": None, "last_price": None}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# ================= دریافت قیمت =================
async def get_gold_price():
    url = "https://milli.gold"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                text = await response.text()

        import re
        match = re.search(r'(\d{1,3}(?:,\d{3})+)', text)
        if match:
            return int(match.group(1).replace(",", ""))
        return None
    except:
        return None

# ================= بررسی قیمت =================
async def check_price():
    data = load_data()
    new_price = await get_gold_price()

    if not new_price:
        return

    last_price = data.get("last_price")

    if not last_price:
        data["last_price"] = new_price
        save_data(data)
        return

    difference = abs(new_price - last_price)

    # ارسال تغییر عادی
    if new_price != last_price:
        await bot.send_message(
            CHANNEL_ID,
            f"💰 قیمت جدید: {new_price:,} تومان"
        )

    # هشدار اختلاف زیاد
    if difference >= PRICE_THRESHOLD:
        await bot.send_message(
            CHANNEL_ID,
            f"🚨 هشدار تغییر شدید قیمت!\nاختلاف: {difference:,} تومان"
        )

    data["last_price"] = new_price
    save_data(data)

# ================= کیبورد =================
def keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("1 دقیقه", callback_data="1"),
        InlineKeyboardButton("5 دقیقه", callback_data="5"),
        InlineKeyboardButton("10 دقیقه", callback_data="10"),
        InlineKeyboardButton("15 دقیقه", callback_data="15"),
        InlineKeyboardButton("⛔ توقف", callback_data="stop"),
    )
    return kb

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("بازه ارسال را انتخاب کنید:", reply_markup=keyboard())

@dp.callback_query_handler()
async def callback_handler(callback: types.CallbackQuery):
    data = load_data()

    if callback.data == "stop":
        scheduler.remove_all_jobs()
        data["interval"] = None
        save_data(data)
        await callback.message.answer("⛔ متوقف شد")
        await callback.answer()
        return

    interval = int(callback.data)

    scheduler.remove_all_jobs()
    scheduler.add_job(check_price, "interval", minutes=interval)

    data["interval"] = interval
    save_data(data)

    await callback.message.answer(f"✅ هر {interval} دقیقه فعال شد")
    await callback.answer()

async def on_startup(dp):
    scheduler.start()
    data = load_data()
    if data.get("interval"):
        scheduler.add_job(check_price, "interval", minutes=data["interval"])

if __name__ == "__main__":
    Thread(target=run_web).start()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
