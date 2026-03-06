from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    # PostgreSQL
    database_url: str = "postgresql://praxisiq:praxisiq_dev@localhost:5433/praxisiq"

    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "praxisiq"
    minio_use_ssl: bool = False

    # Embeddings
    embedding_provider: str = "voyage"
    voyage_api_key: str = ""
    embedding_model: str = "voyage-3"
    embedding_dimensions: int = 1024

    # Pipeline
    confidence_high_threshold: float = 0.85
    confidence_medium_threshold: float = 0.60
    chunk_size: int = 512
    chunk_overlap: int = 50

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
