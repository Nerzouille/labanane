from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    cors_origins: list[str] = ["http://localhost:5173"]
    source_timeout: int = 10  # seconds per data source

    model_config = {"env_file": ".env", "env_prefix": "APP_", "extra": "ignore"}


settings = Settings()
