"""
Вызов сторонних API (минимум 2 по заданию).
"""
import logging
import requests

logger = logging.getLogger('museum')

# Внешние API (публичные, без ключа)
EXTERNAL_API_1_URL = 'https://jsonplaceholder.typicode.com/posts/1'  # Пример поста
EXTERNAL_API_2_URL = 'https://api.quotable.io/random'  # Случайная цитата


def fetch_external_api_1():
    """Первый сторонний API: JSONPlaceholder — пример поста."""
    try:
        r = requests.get(EXTERNAL_API_1_URL, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.warning('External API 1 failed: %s', e)
        return {'error': str(e), 'title': '', 'body': ''}


def fetch_external_api_2():
    """Второй сторонний API: Quotable — случайная цитата."""
    try:
        r = requests.get(EXTERNAL_API_2_URL, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.warning('External API 2 failed: %s', e)
        return {'error': str(e), 'content': '', 'author': ''}
