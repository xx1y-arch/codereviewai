import typing as t
from linecache import cache

import httpx

from collections import UserList
from dataclasses import dataclass

from app.configs import GitHubConfig
from app.exceptions import GitHubServiceError
from app.http_client import HttpClientWithInterceptors
from app.interceptors import RetryInterceptor, LoggingInterceptor
from app.interceptors.retry_strategies import RateLimitRetryStrategy
from app.services import BaseService


@dataclass
class File:
    name: str
    content: str


class GitHubContent(t.TypedDict):
    type: str
    path: str
    sha: str
    size: int
    url: str
    download_url: t.Optional[str]


GitHubResponse = t.List[GitHubContent]

class FileList(UserList[File]):

    @property
    def names(self):
        return [file.name for file in self]


class GitHubService(BaseService):
    CONFIG = GitHubConfig

    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.headers = {
            "Authorization": f"token {self.api_key}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "CodeReviewAI/1.0 (https://example.com)"
        }
        self.http_client = HttpClientWithInterceptors([
            LoggingInterceptor(),
            RetryInterceptor(RateLimitRetryStrategy())
        ])

    async def execute(self, repo_url: str) -> FileList:
        repo_name = repo_url.split("github.com/")[1]
        url = f"{self.CONFIG.API_URL}/repos/{repo_name}/contents/"
        return await self._fetch_contents_recursive(url)

    async def _fetch_contents_recursive(self, url: str) -> FileList:
        request = httpx.Request(
            method="GET",
            url=url,
            headers=self.headers
        )
        response = await self.http_client.send(request)

        if response.status_code != 200:
            raise GitHubServiceError(
                f"GitHub API error: {response.status_code} - {response.text}"
            )

        files = []
        contents = response.json()

        for item in contents:
            if item["type"] == "file":
                files.append(
                    File(
                        name=item["path"],
                        content=await self._fetch_file_content(
                            item["download_url"]
                        )
                    )
                )
            elif item["type"] == "dir":
                files.extend(
                    await self._fetch_contents_recursive(item["url"])
                )

        return FileList(files)

    async def _fetch_file_content(self, download_url: str) -> str:
        request = httpx.Request(
            method="GET",
            url=download_url,
            headers=self.headers
        )
        response = await self.http_client.send(request)
        if response.status_code != 200:
            raise GitHubServiceError(
                f"Error fetching file content:"
                f" {response.status_code} - {response.text}"
            )
        return response.text

    async def parse(self, response: GitHubResponse) -> FileList:
        files = []

        for item in response:
            if item["type"] == "file":
                files.append(
                    File(
                        name=item["path"],
                        content=(
                            await self._fetch_file_content(item["download_url"])
                        )
                    )
                )
            elif item["type"] == "dir":
                files.extend(await self._fetch_file_content(item["url"]))

        return FileList(files)
