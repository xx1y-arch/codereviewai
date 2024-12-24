import hashlib
import json
import os

import redis

from functools import wraps

DEFAULT_CACHE_TIME = 60 * 60


class UniversalJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "to_dict"):
            return obj.to_dict()

        if hasattr(obj, "__dict__"):
            return obj.__dict__

        return str(obj)


def get_redis_client() -> redis.Redis:
    from app.main import redis_client

    if not redis_client:
        raise RuntimeError(
            "Redis client is not initialized."
        )
    return redis_client


def redis_cache(ttl: int = DEFAULT_CACHE_TIME):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):

            if os.getenv("TEST"):
                return await func(*args, **kwargs)

            client = get_redis_client()

            try:
                kwargs_serialized = json.dumps(kwargs, sort_keys=True)
            except TypeError as e:
                raise ValueError(f"Cannot serialize kwargs: {kwargs}. Error: {e}")

            cache_key = f"{func.__name__}:{hashlib.md5(kwargs_serialized.encode()).hexdigest()}"
            cached_data = client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)

            result = await func(*args, **kwargs)

            client.set(
                cache_key,
                json.dumps(result, cls=UniversalJSONEncoder),
                ex=ttl
            )
            return result

        return wrapper

    return decorator
