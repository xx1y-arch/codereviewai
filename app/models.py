import re
import typing as t

from pydantic import BaseModel, field_validator

from app.enums import CandidateLevel

GITHUB_URL_PATTERN = r"^https://github\.com/[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$"


class ReviewRequest(BaseModel):
    assignment_description: str
    github_repo_url: str
    candidate_level: CandidateLevel

    @field_validator("github_repo_url")
    @classmethod
    def validate_github_url(cls, value: str) -> str:
        if not re.match(GITHUB_URL_PATTERN, value):
            raise ValueError(f"Invalid GitHub repository URL: {value}")
        return value


class ReviewResponse(BaseModel):
    review: str
    files: t.List[str]

    def to_dict(self):
        return {
            "review": self.review,
            "files": self.files,
        }


