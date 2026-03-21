from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    event_count: int = 5
    event_interval: float = 1.5
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = {"env_file": ".env", "env_prefix": "APP_"}


settings = Settings()
