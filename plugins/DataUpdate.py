import nonebot
import aiohttp
from datetime import datetime


@nonebot.scheduler.scheduled_job('cron', minute='15, 45')
async def _():
    async with aiohttp.request('GET', 'https://api.matsurihi.me/mltd/v1/events') as resp:
        json = await resp.json()
        t = json[-1]['type']
        time = json[-1]['schedule']['endDate']


