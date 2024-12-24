from fastapi import HTTPException


class OpenAIServiceError(Exception):
    pass


class GitHubServiceError(Exception):
    pass


class UseCaseException(HTTPException):
    pass


class ValidationError(HTTPException):

    def __init__(self, detail: str):
        super().__init__(status_code=422, detail=detail)
