import aiohttp
import asyncio
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

# ===================== تنظیمات =====================
BOT_TOKEN = "8400605005:AAHSCRVbw1FfQs5fPm5UKdng4N9jh6HOH0M"
CHANNEL_ID = "@miliichanel"  # حتما @ اول باشه
URL = "https://milli.gold/"

# ===================== وب سرور برای Always-On =====================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

Thread(target=lambda: app.run(host="0.0.0.0", port=3000)).start()

# ===================== دریافت نرخ طلای ۱۸ عیار =====================
async def get_gold_price():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(URL) as response:
                html = await response.text()

        soup = BeautifulSoup(html, "html.parser")
        
        # پیدا کردن نرخ طلای ۱۸ عیار
        # بررسی تمام span یا divها که شامل "18 عیار" هستند
        price_text = None
        for tag in soup.find_all(["span", "div"]):
            if tag.text and "۱۸ عیار" in tag.text:
                import re
                match = re.search(r'(\d{1,3}(?:,\d{3})+)', tag.text)
                if match:
                    price_text = match.group(1)
                    break

        if price_text:
            return int(price_text.replace(",", ""))
        return None

    except Exception as e:
        print("Error fetching price:", e)
        return None

# ===================== ارسال پیام Telegram =====================
async def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": text}
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(url, data=payload)
    except Exception as e:
        print("Error sending message:", e)

# ===================== اجرای اصلی =====================
async def main():
    # ارسال فوری اولین پیام
    price = await get_gold_price()
    if price:
        await send_message(f"💰 نرخ طلای ۱۸ عیار: {price:,} ریال")
        print(f"✅ پیام ارسال شد: {price:,} ریال")
    else:
        print("⚠️ قیمت پیدا نشد")

    # حلقه تکرار هر ۵ دقیقه
    while True:
        await asyncio.sleep(300)
        price = await get_gold_price()
        if price:
            await send_message(f"💰 نرخ طلای ۱۸ عیار: {price:,} ریال")
            print(f"✅ پیام ارسال شد: {price:,} ریال")
        else:
            print("⚠️ قیمت پیدا نشد")

if __name__ == "__main__":
    asyncio.run(main())
