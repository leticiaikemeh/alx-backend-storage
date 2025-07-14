#!/usr/bin/env python3
"""
Module to define a Cache class for storing data in Redis.
"""

import uuid
import functools
from typing import Callable, Optional, Union
import redis

def count_calls(method: Callable) -> Callable:
    """Decorator to count how many times a method is called."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        key = method.__qualname__
        self._redis.incr(key)           # pylint: disable=protected-access
        return method(self, *args, **kwargs)
    return wrapper

def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and outputs for a function.
    Stores inputs in <qualname>:inputs and outputs in <qualname>:outputs
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"
        # Store input arguments as a string in the inputs list
        self._redis.rpush(input_key, str(args))     # pylint: disable=protected-access
        # Call the actual method and store the output
        output = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(output))  # pylint: disable=protected-access
        return output
    return wrapper

class Cache:
    """Cache class for storing data in Redis."""

    def __init__(self):
        """Initialize Redis client and flush the database."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
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

def replay(method: Callable):
    """
    Display the history of calls of a particular function.
    Shows number of calls, inputs, and outputs.
    """
    redis_client = method.__self__._redis  # pylint: disable=protected-access
    qualname = method.__qualname__
    calls = redis_client.get(qualname)
    try:
        calls_count = int(calls.decode("utf-8")) if calls else 0
    except Exception:
        calls_count = 0
    print(f"{qualname} was called {calls_count} times:")
    inputs = redis_client.lrange(f"{qualname}:inputs", 0, -1)
    outputs = redis_client.lrange(f"{qualname}:outputs", 0, -1)
    for inp, outp in zip(inputs, outputs):
        print(f"{qualname}(*{inp.decode('utf-8')}) -> {outp.decode('utf-8')}")
