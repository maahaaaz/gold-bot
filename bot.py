import os
import json
import aiohttp
import asyncio
import re

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

DATA_FILE = "data.json"
PRICE_THRESHOLD = 50000  # اختلاف برای هشدار شدید

# ================= مدیریت فایل =================
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"last_price": None}
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

        match = re.search(r'(\d{1,3}(?:,\d{3})+)', text)
        if match:
            return int(match.group(1).replace(",", ""))
        return None
    except:
        return None

# ================= ارسال پیام =================
async def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text
    }
    async with aiohttp.ClientSession() as session:
        await session.post(url, data=payload)

# ================= اجرای اصلی =================
async def main():
    data = load_data()
    last_price = data.get("last_price")

    new_price = await get_gold_price()

    if not new_price:
        print("Price not found")
        return

    if not last_price:
        data["last_price"] = new_price
        save_data(data)
        print("First run - price saved")
        return

    difference = abs(new_price - last_price)

    # تغییر قیمت
    if new_price != last_price:
        await send_message(f"💰 قیمت جدید طلای ۱۸ عیار:\n{new_price:,} تومان")

    # هشدار اختلاف شدید
    if difference >= PRICE_THRESHOLD:
        await send_message(
            f"🚨 هشدار تغییر شدید قیمت!\nاختلاف: {difference:,} تومان"
        )

    data["last_price"] = new_price
    save_data(data)

if __name__ == "__main__":
    asyncio.run(main())
