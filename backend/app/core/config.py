from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "DocTalk AI"
    DEBUG: bool = False

    # Auth
    SECRET_KEY: str = "change-me-in-production-use-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    DATABASE_URL: str = "sqlite:///./doctalk.db"

    # Gemini / Google API
    # ✅ Must stay as plain `str` — NOT SecretStr.
    # langchain_google_genai reads GOOGLE_API_KEY directly from os.environ
    # via its own internal Pydantic v1 model and wraps it in SecretStr,
    # which breaks gRPC (grpc expects str, not SecretStr).
    # We force it to plain str in main.py before any langchain import.
    GOOGLE_API_KEY: str = ""

    # HR Contact
    HR_CONTACT_EMAIL: str = "hr@yourcompany.com"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Storage
    VECTOR_STORE_PATH: str = "./vector_store"
    UPLOAD_DIR: str = "./uploads"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()