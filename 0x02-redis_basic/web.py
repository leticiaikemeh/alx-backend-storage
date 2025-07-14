#!/usr/bin/env python3
"""
Web caching and access counter using Redis.
"""

from typing import Callable
from functools import wraps
import redis
import requests

redis_client = redis.Redis()

def cache_page(expiration: int = 10):
    """
    Decorator to cache the content of a web page for a set expiration time.
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(url: str) -> str:
            cache_key = f"cached:{url}"
            cached_content = redis_client.get(cache_key)
            if cached_content:
                return cached_content.decode('utf-8')
            # Not cached, fetch and cache it
            content = func(url)
            redis_client.setex(cache_key, expiration, content)
            return content
        return wrapper
    return decorator

@cache_page(expiration=10)
def get_page(url: str) -> str:
    """
    Get HTML content of the URL and track access count. Cache the result.
    """
    # Track count
    redis_client.incr(f"count:{url}")
    # Fetch page
    response = requests.get(url)
    return response.text

if __name__ == "__main__":
    TEST_URL = "http://slowwly.robertomurray.co.uk"
    print(get_page(TEST_URL))
    print("Access count:", int(redis_client.get(f"count:{TEST_URL}")))
