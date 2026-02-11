import aiohttp
import asyncio
from flask import Flask
from threading import Thread

# ===================== تنظیمات =====================
BOT_TOKEN = "8400605005:AAHSCRVbw1FfQs5fPm5UKdng4N9jh6HOH0M"
CHANNEL_ID = "@miliichanel"

# ⚠️ API داخلی میلی‌گلد (اینو تست کن)
API_URL = "https://api.milli.gold/api/v1/gold"

# ===================== وب سرور برای Always-On =====================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

Thread(target=lambda: app.run(host="0.0.0.0", port=3000)).start()

# ===================== گرفتن نرخ واقعی =====================
async def get_gold_price():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL) as response:
                data = await response.json()

        # پیدا کردن طلای 18 عیار داخل JSON
        # ساختار احتمالی:
        # data["data"] لیست آبجکت‌هاست
        for item in data.get("data", []):
            if "18" in item.get("name", ""):
                return int(item.get("price"))

        return None

    except Exception as e:
        print("Error fetching API:", e)
        return None

# ===================== ارسال پیام =====================
async def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": text}
    async with aiohttp.ClientSession() as session:
        await session.post(url, data=payload)

# ===================== اجرای اصلی =====================
async def main():
    while True:
        price = await get_gold_price()

        if price:
            await send_message(f"💰 نرخ طلای ۱۸ عیار: {price:,} ریال")
            print("✅ ارسال شد:", price)
        else:
            print("⚠️ قیمت پیدا نشد")

        await asyncio.sleep(300)  # هر ۵ دقیقه

if __name__ == "__main__":
    asyncio.run(main())
