"""Embedding and vector store helpers."""

from __future__ import annotations

from pathlib import Path
import time

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from backend.config import settings


def get_embeddings() -> OpenAIEmbeddings:
    """Return the configured embeddings client."""
    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is required to build embeddings for the MVP index."
        )

    return OpenAIEmbeddings(
        model=settings.openai_embedding_model,
        api_key=settings.openai_api_key,
    )


def build_faiss_index(documents: list[Document]) -> FAISS:
    """Build a FAISS vector store from documents."""
    embeddings = get_embeddings()
    return FAISS.from_documents(documents, embeddings)


def build_faiss_index_batched(
    documents: list[Document],
    batch_size: int,
    sleep_seconds: float = 0.0,
) -> FAISS:
    """Build a FAISS vector store in batches to control request rate."""
    if not documents:
        raise ValueError("No documents provided for embedding.")

    if batch_size <= 0:
        raise ValueError("batch_size must be a positive integer.")

    embeddings = get_embeddings()
    first_batch = documents[:batch_size]
    vectorstore = FAISS.from_documents(first_batch, embeddings)

    if sleep_seconds > 0 and len(documents) > batch_size:
        time.sleep(sleep_seconds)

    for start in range(batch_size, len(documents), batch_size):
        batch = documents[start : start + batch_size]
        vectorstore.add_documents(batch)
        if sleep_seconds > 0 and start + batch_size < len(documents):
            time.sleep(sleep_seconds)

    return vectorstore


def save_faiss_index(vectorstore: FAISS, target_dir: Path) -> None:
    """Persist the FAISS vector store to disk."""
    target_dir.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(target_dir))


def load_faiss_index(index_dir: Path) -> FAISS:
    """Load a persisted FAISS vector store."""
    embeddings = get_embeddings()
    if not index_dir.exists():
        raise FileNotFoundError(
            f"Vector index not found at '{index_dir}'. Run ingestion first."
        )

    return FAISS.load_local(
        str(index_dir),
        embeddings,
        allow_dangerous_deserialization=True,
    )
