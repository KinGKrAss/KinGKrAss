from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Z1 Löwenherz Operating System"
    app_env: str = "development"
    app_debug: bool = True
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60
    database_url: str = "sqlite+pysqlite:///./z1.db"
    redis_url: str = "redis://localhost:6379/0"
    openai_api_base: str = "https://api.openai.com/v1"
    openai_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
