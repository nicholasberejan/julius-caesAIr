"""Central application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Typed settings loaded from environment variables."""

    project_root: Path = Path(__file__).resolve().parent.parent
    flask_env: str = os.getenv("FLASK_ENV", "development")
    flask_debug: bool = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    flask_host: str = os.getenv("FLASK_HOST", "127.0.0.1")
    flask_port: int = int(os.getenv("FLASK_PORT", "5000"))
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY") or None
    openai_chat_model: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
    openai_embedding_model: str = os.getenv(
        "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
    )
    embedding_cost_per_1m_tokens: float = float(
        os.getenv("EMBEDDING_COST_PER_1M_TOKENS", "0.02")
    )
    source_docs_dir: Path = project_root / os.getenv("SOURCE_DOCS_DIR", "data/raw")
    vector_index_dir: Path = project_root / os.getenv(
        "VECTOR_INDEX_DIR", "data/indexes/caesar_faiss"
    )
    default_top_k: int = int(os.getenv("DEFAULT_TOP_K", "4"))
    max_chunk_size: int = int(os.getenv("MAX_CHUNK_SIZE", "1200"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "150"))
    ingest_batch_size: int = int(os.getenv("INGEST_BATCH_SIZE", "64"))
    ingest_sleep_seconds: float = float(os.getenv("INGEST_SLEEP_SECONDS", "0.0"))
    ingest_max_pages_per_pdf: int | None = (
        int(os.getenv("INGEST_MAX_PAGES_PER_PDF", "0")) or None
    )
    ingest_max_chunks: int | None = (
        int(os.getenv("INGEST_MAX_CHUNKS", "0")) or None
    )
    retrieval_relevance_threshold: float = float(
        os.getenv("RETRIEVAL_RELEVANCE_THRESHOLD", "0.6")
    )
    retrieval_utility_threshold: float = float(
        os.getenv("RETRIEVAL_UTILITY_THRESHOLD", "0.6")
    )
    grader_max_retries: int = int(os.getenv("GRADER_MAX_RETRIES", "2"))


settings = Settings()
