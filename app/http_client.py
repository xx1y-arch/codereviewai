import httpx

from app.interceptors import BaseInterceptor



class HttpClientWithInterceptors:

    def __init__(self, interceptors: list[BaseInterceptor]):
        self.interceptors = interceptors

    async def send(self, request: httpx.Request) -> httpx.Response:
        async def call_next(index: int, req: httpx.Request):
            return await self.interceptors[index].intercept(
                req, lambda: call_next(index + 1, req)
            )

        return await call_next(0, request)
