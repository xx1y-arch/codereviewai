import httpx
import typing as t

from app.interceptors.abc import BaseInterceptor


class LoggingInterceptor(BaseInterceptor):
    async def intercept(
        self,
        request: httpx.Request,
        call_next: t.Callable[[], t.Coroutine[None, None, httpx.Response]]
    ) -> httpx.Response:
        from app.logger import get_logger

        logger = get_logger("LoggingInterceptor")
        logger.info(f"Sending {request.method} request to {request.url}")

        response = await call_next()

        logger.info(f"Received response with status code {response.status_code} from {request.url}")
        return response
