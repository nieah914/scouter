from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = ""

    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""

    # Toss Payments
    toss_client_key: str = ""
    toss_secret_key: str = ""
    toss_webhook_secret: str = ""

    # 공공데이터 포털
    public_data_api_key: str = ""

    # App
    app_env: str = "development"
    secret_key: str = "dev-secret-key"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
