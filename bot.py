import aiohttp
import asyncio
import re
from flask import Flask
from threading import Thread
from bs4 import BeautifulSoup

# ===================== تنظیمات =====================
BOT_TOKEN = "8400605005:AAHSCRVbw1FfQs5fPm5UKdng4N9jh6HOH0M"
CHANNEL_ID = "@miliichanel"  # حتما @ اول باشه

# ===================== وب سرور برای Always-On =====================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

Thread(target=lambda: app.run(host="0.0.0.0", port=3000)).start()

# ===================== دریافت نرخ طلا =====================
async def get_gold_price():
    url = "https://milli.gold/"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                text = await response.text()

        soup = BeautifulSoup(text, "html.parser")

        # پیدا کردن بخش قیمت طلای 18 عیار
        price_tag = soup.find("div", string=lambda s: s and "قیمت" in s and "۱۸ عیار" in s)
        if price_tag:
            match = re.search(r'(\d{1,3}(?:,\d{3})+)', price_tag.text)
            if match:
                return int(match.group(1).replace(",", ""))

        return None
    except Exception as e:
        print("Error parsing price:", e)
        return None

# ===================== ارسال پیام =====================
async def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text
    }
    async with aiohttp.ClientSession() as session:
        await session.post(url, data=payload)

# ===================== اجرای اصلی =====================
async def main():
    while True:
        price = await get_gold_price()
        if price:
            await send_message(f"💰 نرخ طلای ۱۸ عیار: {price:,} ریال")
            print(f"✅ پیام ارسال شد: {price:,} ریال")
        else:
            print("⚠️ قیمت پیدا نشد")
        await asyncio.sleep(300)  # هر ۵ دقیقه

if __name__ == "__main__":
    asyncio.run(main())
