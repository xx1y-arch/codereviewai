from app.cache import redis_cache
from app.exceptions import UseCaseException
from app.models import ReviewResponse
from app.services.openai_service import OpenAIService
from app.services.github_service import GitHubService


class CodeReviewUseCase:
    def __init__(
        self,
        github_service: GitHubService,
        openai_service: OpenAIService
    ):
        self.github_service = github_service
        self.openai_service = openai_service

    @redis_cache(ttl=60)
    async def execute(
        self,
        repo_url: str,
        description: str,
        candidate_level: str
    ) -> ReviewResponse:
        files = await self.github_service.execute(repo_url)
        if not files:
            raise UseCaseException(
                status_code=404,
                detail="No files found in repository."
            )

        review = await self.openai_service.execute(
            description, files, candidate_level
        )

        return ReviewResponse(
            review=review,
            files=files.names
        )
