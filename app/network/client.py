import aiohttp
import asyncio

async def fetch_data_async(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                resp.raise_for_status()
                data = await resp.text()
                return data
    except Exception as e:
        return f"请求失败: {e}" 