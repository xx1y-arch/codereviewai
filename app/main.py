import logging
import os

import redis
import typing as t

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends

from app.models import ReviewRequest, ReviewResponse
from app.services import GitHubService, OpenAIService
from app.usecase import CodeReviewUseCase

logger = logging.getLogger(__name__)

redis_client = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> t.AsyncGenerator[None, None]:
    global redis_client
    redis_client = redis.from_url(
        url=os.getenv("REDIS_URL"), decode_responses=True
    )
    logger.info("Redis connection established")

    yield

    redis_client.close()
    logger.info("Redis connection closed")


def get_github_service() -> GitHubService:
    return GitHubService(api_key=os.getenv("GITHUB_API_KEY"))


def get_openai_service() -> OpenAIService:
    return OpenAIService(api_key=os.getenv("OPENAI_API_KEY"))


def get_code_review_usecase(
    github_service: GitHubService = Depends(get_github_service),
    openai_service: OpenAIService = Depends(get_openai_service)
) -> CodeReviewUseCase:
    return CodeReviewUseCase(github_service, openai_service)


app = FastAPI(title="Auto-Review Tool", lifespan=lifespan)


@app.post(
    "/review",
    response_model=ReviewResponse,
)
async def review_code(
    request: ReviewRequest,
    use_case: CodeReviewUseCase = Depends(get_code_review_usecase),
) -> ReviewResponse:
    try:
        result = await use_case.execute(
            repo_url=request.github_repo_url,
            description=request.assignment_description,
            candidate_level=request.candidate_level.value
        )
        logger.info(
            f"Review for {str(request.github_repo_url)} completed."
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
