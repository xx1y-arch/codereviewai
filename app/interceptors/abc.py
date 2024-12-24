import httpx
import typing as t

from abc import ABC, abstractmethod


class BaseInterceptor(ABC):
    @abstractmethod
    async def intercept(
        self,
        request: httpx.Request,
        call_next: t.Callable[[], httpx.Response],
    ) -> httpx.Response:
        ...
