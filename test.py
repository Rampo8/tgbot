import asyncio, aiohttp

async def main():
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as s:
        try:
            async with s.get("https://api.telegram.org") as r:
                print(f"✅ Telegram доступен! Статус: {r.status}")
        except:
            print("❌ Telegram НЕ доступен — включите VPN на телефоне")

asyncio.run(main())