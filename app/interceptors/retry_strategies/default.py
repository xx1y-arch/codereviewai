import httpx
import typing as t

from app.interceptors.retry_strategies.abc import RetryStrategy


class DefaultRetryStrategy(RetryStrategy):

    def __init__(self, backoff_factor: float = 2.0, max_retries: int = 3):
        self.backoff_factor = backoff_factor
        self.max_retries = max_retries

    async def should_retry(self, response: httpx.Response, attempt: int) -> t.Tuple[bool, int]:
        return bool(response.status_code >= 500 and attempt < self.max_retries), 0

    async def get_backoff_time(self, response: httpx.Response, attempt: int) -> float:
        return self.backoff_factor ** attempt
