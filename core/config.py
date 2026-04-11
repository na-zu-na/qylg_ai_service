import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "ai-service")
    APP_PORT: int = int(os.getenv("APP_PORT", "9000"))
    APP_ENV: str = os.getenv("APP_ENV", "dev")

    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")


settings = Settings()