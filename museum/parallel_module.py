"""
Модуль для работы с параллельным кодом (asyncio).
Параллельный запрос к нескольким внешним API для ускорения страницы «Внешние API».
"""
import asyncio
import logging
from typing import Any, Dict, List, Tuple

import aiohttp

logger = logging.getLogger('museum')

EXTERNAL_API_1_URL = 'https://jsonplaceholder.typicode.com/posts/1'
EXTERNAL_API_2_URL = 'https://api.quotable.io/random'


async def fetch_one(session: aiohttp.ClientSession, url: str, name: str) -> Dict[str, Any]:
    """Асинхронный запрос к одному API."""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return {'name': name, 'data': data, 'error': None}
    except Exception as e:
        logger.warning('Async fetch %s failed: %s', name, e)
        return {'name': name, 'data': None, 'error': str(e)}


async def fetch_all_async() -> List[Dict[str, Any]]:
    """Параллельно запрашивает оба внешних API (asyncio)."""
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_one(session, EXTERNAL_API_1_URL, 'api1'),
            fetch_one(session, EXTERNAL_API_2_URL, 'api2'),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        return list(results)


def fetch_external_apis_parallel() -> Tuple[Dict, Dict]:
    """
    Синхронная обёртка: запускает параллельные запросы через asyncio
    и возвращает (результат_api1, результат_api2) в формате, совместимом с external_apis_view.
    """
    results = asyncio.run(fetch_all_async())
    api1 = results[0]
    api2 = results[1]

    def to_api1_format(r: Dict) -> Dict:
        if r.get('error') or not r.get('data'):
            return {'error': r.get('error', 'Unknown'), 'title': '', 'body': ''}
        d = r['data']
        return {'title': d.get('title', ''), 'body': d.get('body', ''), 'error': None}

    def to_api2_format(r: Dict) -> Dict:
        if r.get('error') or not r.get('data'):
            return {'error': r.get('error', 'Unknown'), 'content': '', 'author': ''}
        d = r['data']
        return {'content': d.get('content', ''), 'author': d.get('author', ''), 'error': None}

    return (to_api1_format(api1), to_api2_format(api2))
