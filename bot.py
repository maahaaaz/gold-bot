import os
import aiohttp
import asyncio
import re

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

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
    price = await get_gold_price()
    if not price:
        print("⚠️ قیمت پیدا نشد")
        return

    # پیام هر بار ارسال می‌شود
    await send_message(f"💰 نرخ طلای ۱۸ عیار: {price:,} تومان")
    print(f"✅ پیام ارسال شد: {price:,} تومان")

if __name__ == "__main__":
    asyncio.run(main())
