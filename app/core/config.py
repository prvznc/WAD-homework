from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "WAD LLM Chat"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    database_url: str = "postgresql+psycopg2://wad:wad@localhost:5432/wad"
    redis_url: str = "redis://localhost:6379/0"

    github_client_id: str = ""
    github_client_secret: str = ""
    github_callback_url: str = "http://localhost:8000/api/auth/github/callback"

    model_path: str = "model.gguf"
    llm_n_ctx: int = 1024
    llm_n_threads: int = 4

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
