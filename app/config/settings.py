from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API Configuration
    app_name: str = "Stock Due Diligence API"
    app_version: str = "1.0.0"
    debug: bool = False

    # DigitalOcean GenAI Agent - Quick Analysis
    stock_agent_key: str
    agent_endpoint: str

    # DigitalOcean GenAI Agent - Deep Research
    deep_agent_key: str
    deep_endpoint: str

    # Tavily Search API
    tavily_api_key: str

    # CORS Origins (comma-separated for multiple origins)
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # Rate Limiting
    rate_limit_per_minute: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
