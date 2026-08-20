from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str

    LLM_PROVIDER: str = "gemini"
    LLM_API_KEY: str
    LLM_MODEL: str = "gemini-1.5-flash"

    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHROMA_PERSIST_DIRECTORY: str = "data/chroma"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/postgres"

    LOG_LEVEL: str = "INFO"
    MAX_UPLOAD_SIZE_MB: int = 20
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    RETRIEVAL_TOP_K: int = 5
    RELEVANCE_THRESHOLD: float = 0.35

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
