import httpx
import typing as t

from abc import ABC, abstractmethod


class RetryStrategy(ABC):

    @abstractmethod
    async def should_retry(
        self,
        response: httpx.Response,
        attempt: int
    ) -> t.Tuple[bool, int]:
        pass

    @abstractmethod
    async def get_backoff_time(
        self,
        response: httpx.Response,
        attempt: int
    ) -> float:
        pass
