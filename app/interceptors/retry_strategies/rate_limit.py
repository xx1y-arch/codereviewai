import httpx
import time
import typing as t

from app.interceptors.retry_strategies import RetryStrategy


class RateLimitRetryStrategy(RetryStrategy):

    async def should_retry(
        self,
        response: httpx.Response,
        attempt: int
    ) -> t.Tuple[bool, int]:

        if (
            response.status_code == 403
            and "X-RateLimit-Remaining" in response.headers
        ):
            remaining = int(response.headers["X-RateLimit-Remaining"])
            if remaining == 0 and "X-RateLimit-Reset" in response.headers:
                reset_time = int(response.headers["X-RateLimit-Reset"])
                time_remaining = max(0, reset_time - time.time())
                return True, time_remaining

        return False, 0

    async def get_backoff_time(
        self,
        response: httpx.Response,
        attempt: int
    ) -> float:
        _, time_remaining = await self.should_retry(response, attempt)
        return time_remaining
