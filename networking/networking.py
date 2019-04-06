import asyncio
import json
import logging
import re
import async_timeout

import aiohttp
from unidecode import unidecode


async def fetch(url, session):
    #print(f"url: {url}")
    try:
        with async_timeout.timeout(5):
            async with session.get(url) as response:
                text = await response.text()
                return text

    except Exception:
        #print(f"Server timeout/error to {url}")
        #logging.exception(f"Server timeout/error to {url}")
        return ""


async def get_responses(urls, timeout, myheaders):
    tasks = []
    async with aiohttp.ClientSession(headers=myheaders) as session:
        for url in urls:
            task = asyncio.ensure_future(fetch(url, session))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        return responses


async def get_response(url, timeout, myheaders):
    async with aiohttp.ClientSession(headers=myheaders) as session:
        response = await fetch(url, session)
        return response
