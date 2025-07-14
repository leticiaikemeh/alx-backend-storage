#!/usr/bin/env python3
"""
Module to define a Cache class for storing data in Redis.
"""

import uuid
from typing import Callable, Optional, Union
import redis

class Cache:
    """Cache class for storing data in Redis."""

    def __init__(self):
        """Initialize Redis client and flush the database."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis with a random key.

        Args:
            data: Data to store (str, bytes, int, or float).

        Returns:
            The random key as a string.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """
        Get a value from Redis by key, optionally applying a conversion function.

        Args:
            key (str): The Redis key.
            fn (Callable, optional): Function to convert the returned data.

        Returns:
            The data, possibly converted by fn, or None if key doesn't exist.
        """
        value = self._redis.get(key)
        if value is None:
            return None
        if fn is not None:
            return fn(value)
        return value

    def get_str(self, key: str) -> Optional[str]:
        """
        Get a string value from Redis by key.

        Args:
            key (str): The Redis key.

        Returns:
            The value decoded as a UTF-8 string, or None if not found.
        """
        return self.get(key, fn=lambda d: d.decode('utf-8') if d else None)

    def get_int(self, key: str) -> Optional[int]:
        """
        Get an integer value from Redis by key.

        Args:
            key (str): The Redis key.

        Returns:
            The value converted to int, or None if not found.
        """
        return self.get(key, fn=lambda d: int(d) if d else None)

cache = Cache()

TEST_CASES = {
    b"foo": None,  # Should return bytes
    123: int,      # Should return integer
    "bar": lambda d: d.decode("utf-8")  # Should return string
}

for value, fn in TEST_CASES.items():
    key = cache.store(value)
    assert cache.get(key, fn=fn) == value

   