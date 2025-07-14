#!/usr/bin/env python3
"""
Module to define a Cache class for storing data in Redis.
"""

import redis
import uuid
from typing import Union

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
