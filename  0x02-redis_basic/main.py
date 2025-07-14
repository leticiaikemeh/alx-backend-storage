#!/usr/bin/env python3
"""
Main file to test the Cache class.
"""
import redis
from exercise import Cache

cache = Cache()

data = b"hello"
key = cache.store(data)
print(key)  # Should print a random uuid

local_redis = redis.Redis()
print(local_redis.get(key))  # Should print: b'hello'
