"""Text chunking helpers for Caesar's corpus."""

from __future__ import annotations

import re

from langchain.text_splitter import RecursiveCharacterTextSplitter

from backend.config import settings


def normalize_text(text: str) -> str:
    """Normalize extracted PDF text for cleaner chunking."""
    cleaned = text.replace("\x00", " ")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def build_text_splitter() -> RecursiveCharacterTextSplitter:
    """Create the default text splitter used during ingestion."""
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.max_chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
