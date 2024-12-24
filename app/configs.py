from dataclasses import dataclass


@dataclass(frozen=True)
class OpenAIConfig:
    API_URL = "https://api.openai.com/v1/chat/completions"
    MODEL = "gpt-4-turbo"
    MAX_RETRIES = 3
    BACKOFF_FACTOR = 2


@dataclass(frozen=True)
class GitHubConfig:
    API_URL = "https://api.github.com"
    MAX_RETRIES = 3
    BACKOFF_FACTOR = 2
