import asyncio
import httpx
import typing as t

from app.interceptors import BaseInterceptor
from app.interceptors.retry_strategies import RetryStrategy


TIMEOUT_IN_SEC = 60.0  # in seconds, some requests arr so slow


class RetryInterceptor(BaseInterceptor):

    timeout = httpx.Timeout(TIMEOUT_IN_SEC)


    def __init__(self, strategy: RetryStrategy):
        self.strategy = strategy

    async def intercept(
        self,
        request: httpx.Request,
        call_next: t.Callable[[], httpx.Response],
    ) -> httpx.Response:
        attempt = 0

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            while True:
                response = await client.send(request)

                should_retry, time_remaining = await self.strategy.should_retry(
                    response, attempt
                )
                if not should_retry:
                    return response

                attempt += 1
                await asyncio.sleep(time_remaining)
