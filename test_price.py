import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re

async def get_gold_price():
    url = "https://milli.gold/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()
    soup = BeautifulSoup(text, "html.parser")
    print("HTML length:", len(text))  # برای بررسی
    # تست ساده: همه اعداد 3 رقمی با کاما
    match = re.search(r'(\d{1,3}(?:,\d{3})+)', text)
    if match:
        return int(match.group(1).replace(",", ""))
    return None

async def main():
    price = await get_gold_price()
    print("Price:", price)

asyncio.run(main())
