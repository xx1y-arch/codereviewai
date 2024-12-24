import httpx
import logging

from app.exceptions import OpenAIServiceError
from app.logger import get_logger

from app.services.github_service import FileList
from app.configs import OpenAIConfig
from app.interceptors import LoggingInterceptor, RetryInterceptor
from app.interceptors.retry_strategies import DefaultRetryStrategy
from app.services import BaseService

from app.http_client import HttpClientWithInterceptors


logger = logging.getLogger(__name__)


class OpenAIService(BaseService):
    CONFIG = OpenAIConfig

    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.logger = get_logger(__name__)
        self.http_client = HttpClientWithInterceptors([
            LoggingInterceptor(),
            RetryInterceptor(
                strategy=DefaultRetryStrategy(
                    max_retries=self.CONFIG.MAX_RETRIES,
                    backoff_factor=self.CONFIG.BACKOFF_FACTOR
                ),
            )
        ])

    async def execute(
        self,
        description: str,
        files: FileList,
        candidate_level: str
    ) -> str:
        prompt = self._generate_prompt(description, files, candidate_level)
        self.logger.info(
            f"Starting analysis for candidate level: {candidate_level}"
        )

        data = {
            "model": self.CONFIG.MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }

        request = httpx.Request(
            method="POST",
            url=self.CONFIG.API_URL,
            headers=self.headers,
            json=data
        )
        response = await self.http_client.send(request)
        return self.parse(response.json())

    def _generate_prompt(
        self,
        description: str,
        files: FileList,
        candidate_level: str
    ) -> str:
        return f"""
        Assignment: {description}
        Candidate Level: {candidate_level}
        Files: 
        {''.join([f"Filename: {file.name}\nContent:\n{file.content}...\n\n" for file in files])}
        Review the code based on best practices, issues, and areas for improvement.
        """

    @staticmethod
    def parse(response: dict):
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise OpenAIServiceError(
                f"Invalid OpenAI API response structure: {e}"
            )
