from app.cache import redis_cache


async def test_redis_cache_decorator(mocker):

    @redis_cache(ttl=60)
    async def some_cached_function(arg1, /, *, kwarg1=""):
        return arg1

    mock_redis = mocker.patch("app.main.redis_client")
    mock_redis.get.return_value = None
    mock_redis.set.return_value = None

    result = await some_cached_function("arg1", kwarg1="value")

    assert result == "arg1"
    mock_redis.set.assert_called_once()
