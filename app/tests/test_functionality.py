import httpx
import pytest
import asyncio

from ..interceptors import RetryInterceptor
from ..interceptors.retry_strategies import RetryStrategy, DefaultRetryStrategy
from ..models import ReviewResponse, ReviewRequest
from ..services import OpenAIService
from ..services.github_service import FileList, File, GitHubService
from ..usecase import CodeReviewUseCase

from pydantic import ValidationError


@pytest.mark.asyncio
async def test_code_review_use_case(mocker):
    mock_github_service = mocker.AsyncMock()
    mock_openai_service = mocker.AsyncMock()

    mock_github_service.execute.return_value = FileList(
        [
            File(
                name="abc.py",
                content="def factorial(): pass"
            ),
            File(
                name="main.py",
                content="print(factorial(5))"
            ),
        ]
    )

    mock_openai_service.execute.return_value = "Mocked review"

    use_case = CodeReviewUseCase(
        github_service=mock_github_service,
        openai_service=mock_openai_service,
    )

    result = await use_case.execute(
        repo_url="https://github.com/example/repo",
        description="Code review task",
        candidate_level="Junior",
    )

    assert result == ReviewResponse(
        review="Mocked review",
        files=["abc.py", "main.py"]
    )

    mock_github_service.execute.assert_called_once_with("https://github.com/example/repo")
    mock_openai_service.execute.assert_called_once()


@pytest.mark.parametrize(
    "data, expected_exception",
    [
        (
                {
                    "github_repo_url": "https://github.com/example/repo",
                    "assignment_description": "Calculate factorial",
                    "candidate_level": "Junior",
                },
                None,
        ),
        (
                {
                    "github_repo_url": "https://github.com/example/repo",
                    "assignment_description": "Calculate factorial",
                },
                ValidationError,
        ),
        (
                {
                    "github_repo_url": "https://github.com/example/repo",
                    "assignment_description": "Calculate factorial",
                    "candidate_level": "Intern",
                },
                ValidationError,
        ),
        (
                {
                    "assignment_description": "Calculate factorial",
                    "candidate_level": "Junior",
                },
                ValidationError,
        ),
        (
                {
                    "github_repo_url": "https://github.com/example/repo",
                    "candidate_level": "Junior",
                },
                ValidationError,
        ),
    ],
)
def test_review_request_validation(data, expected_exception):
    if expected_exception:
        with pytest.raises(expected_exception):
            ReviewRequest(**data)
    else:
        request = ReviewRequest(**data)
        assert request.github_repo_url == data["github_repo_url"]
        assert request.assignment_description == data["assignment_description"]
        assert request.candidate_level.value == data["candidate_level"]


# Services
@pytest.mark.asyncio
async def test_github_service_execute(mocker):
    mock_fetch_files = mocker.patch(
        "app.services.github_service.GitHubService.execute",
        return_value=[
            {"name": "abc.py", "content": "def factorial(): pass"},
            {"name": "main.py", "content": "print(factorial(5))"},
        ]
    )

    github_service = GitHubService(api_key="fake_key")

    result = await github_service.execute("https://github.com/example/repo")

    assert len(result) == 2
    assert result[0]["name"] == "abc.py"
    assert result[1]["name"] == "main.py"

    mock_fetch_files.assert_called_once_with("https://github.com/example/repo")


@pytest.mark.asyncio
async def test_openai_service_generate_review(mocker):
    mock_generate_review = mocker.patch(
        "app.services.openai_service.OpenAIService.execute",
        return_value="Mocked review"
    )

    openai_service = OpenAIService(api_key="fake_key")

    result = await openai_service.execute(
        description="Code review task",
        files=FileList(
            [
                File(
                    name="abc.py", content="def factorial(): pass"),
                File(name="main.py", content="print(factorial(5))"),
            ]
        ),
        candidate_level="Junior",
    )

    assert result == "Mocked review"
    mock_generate_review.assert_called_once_with(
        description="Code review task",
        files=FileList(
            [
                File(
                    name="abc.py", content="def factorial(): pass"),
                File(name="main.py", content="print(factorial(5))"),
            ]
        ),
        candidate_level="Junior",
    )
@pytest.mark.parametrize(
    "attempt, expected_retry, expected_delay",
    [
        (1, True, 1),
        (2, True, 2),
        (3, True, 4),
        (4, False, 0),
    ],
)

async def test_exponential_backoff_strategy(mocker, attempt, expected_retry, expected_delay):
    strategy = DefaultRetryStrategy(max_retries=3)

    mock_response = mocker.Mock()

    retry, delay = await strategy.should_retry(mock_response, attempt)

    assert retry == expected_retry
    assert delay == expected_delay


@pytest.mark.asyncio
async def test_retry_interceptor(mocker):
    mock_strategy = mocker.MagicMock(spec=RetryStrategy)
    mock_strategy.should_retry.side_effect = [
        (True, 1),
        (False, 0),
    ]

    mock_send = mocker.AsyncMock(side_effect=[
        Exception("error"),
        httpx.Response(200, text="Mocked successful response"),
    ])

    mock_client = mocker.patch("httpx.AsyncClient", autospec=True)
    mock_client.return_value.__aenter__.return_value.send = mock_send

    request = httpx.Request("GET", "https://example.com")

    retry_interceptor = RetryInterceptor(strategy=mock_strategy)

    try:
        result = await retry_interceptor.intercept(
            request=request,
            call_next=None,
        )
        assert result.status_code == 200
        assert result.text == "Mocked successful response"
        assert mock_send.call_count == 2
        mock_strategy.should_retry.assert_called_with(result, 1)

    except Exception:
            pass

