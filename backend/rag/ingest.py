"""PDF ingestion pipeline for building the Caesar corpus index."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from openai import RateLimitError

from langchain_core.documents import Document
from pypdf import PdfReader

from backend.config import settings
from backend.rag.chunking import build_text_splitter, normalize_text
from backend.rag.embeddings import build_faiss_index_batched, save_faiss_index


def extract_pdf_documents(
    pdf_path: Path, max_pages: int | None = None
) -> list[Document]:
    """Extract page-level documents from a single PDF."""
    reader = PdfReader(str(pdf_path))
    documents: list[Document] = []

    for page_number, page in enumerate(reader.pages, start=1):
        if max_pages and page_number > max_pages:
            break
        text = normalize_text(page.extract_text() or "")
        if not text:
            continue

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": pdf_path.name,
                    "page": page_number,
                },
            )
        )

    return documents


def chunk_documents(documents: list[Document]) -> list[Document]:
    """Split documents into retrieval-ready chunks."""
    splitter = build_text_splitter()
    return splitter.split_documents(documents)


def load_source_pdfs(source_dir: Path) -> list[Path]:
    """Return all PDF files found in the configured source directory."""
    return sorted(path for path in source_dir.glob("*.pdf") if path.is_file())


def _limit_chunks(
    documents: list[Document], max_chunks: int | None
) -> list[Document]:
    if not max_chunks:
        return documents
    return documents[:max_chunks]


def _iter_sources(pdf_paths: Iterable[Path], max_pages_per_pdf: int | None) -> list[Document]:
    raw_documents: list[Document] = []
    for pdf_path in pdf_paths:
        raw_documents.extend(extract_pdf_documents(pdf_path, max_pages_per_pdf))
    return raw_documents


def _estimate_tokens(documents: list[Document], model: str) -> tuple[int, str]:
    try:
        import tiktoken  # type: ignore

        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        total = 0
        for doc in documents:
            total += len(encoding.encode(doc.page_content))
        return total, "tiktoken"
    except Exception:
        total_chars = sum(len(doc.page_content) for doc in documents)
        estimated_tokens = max(1, total_chars // 4)
        return estimated_tokens, "chars/4"


def _format_cost(estimated_tokens: int) -> str:
    cost = (estimated_tokens / 1_000_000) * settings.embedding_cost_per_1m_tokens
    return f"${cost:,.4f}"


def ingest_corpus(
    *,
    max_pages_per_pdf: int | None = None,
    max_chunks: int | None = None,
    batch_size: int | None = None,
    sleep_seconds: float | None = None,
    dry_run: bool = False,
) -> None:
    """Extract, chunk, embed, and index the configured corpus."""
    pdf_paths = load_source_pdfs(settings.source_docs_dir)
    if not pdf_paths:
        raise FileNotFoundError(
            f"No PDF files found in '{settings.source_docs_dir}'. Add source files first."
        )

    raw_documents = _iter_sources(
        pdf_paths, max_pages_per_pdf or settings.ingest_max_pages_per_pdf
    )

    if not raw_documents:
        raise ValueError("No extractable text was found in the provided PDF files.")

    chunked_documents = chunk_documents(raw_documents)
    chunked_documents = _limit_chunks(
        chunked_documents, max_chunks or settings.ingest_max_chunks
    )

    if dry_run:
        estimated_tokens, method = _estimate_tokens(
            chunked_documents, settings.openai_embedding_model
        )
        print(f"Dry run: {len(pdf_paths)} PDF(s)")
        print(f"Pages extracted: {len(raw_documents)}")
        print(f"Chunks: {len(chunked_documents)}")
        print(f"Token estimate ({method}): {estimated_tokens:,}")
        print(
            f"Estimated embed cost at ${settings.embedding_cost_per_1m_tokens}/1M tokens: "
            f"{_format_cost(estimated_tokens)}"
        )
        return

    resolved_batch_size = batch_size or settings.ingest_batch_size
    resolved_sleep = (
        sleep_seconds if sleep_seconds is not None else settings.ingest_sleep_seconds
    )

    try:
        vectorstore = build_faiss_index_batched(
            chunked_documents,
            batch_size=resolved_batch_size,
            sleep_seconds=resolved_sleep,
        )
        save_faiss_index(vectorstore, settings.vector_index_dir)
    except RateLimitError as exc:
        message = str(exc)
        if "insufficient_quota" in message:
            raise RuntimeError(
                "Embedding failed due to insufficient OpenAI quota. "
                "Check your OpenAI usage/billing limits or add credits, then retry."
            ) from exc
        raise RuntimeError(
            "Embedding failed due to OpenAI rate limits. "
            "Try reducing INGEST_BATCH_SIZE, increasing INGEST_SLEEP_SECONDS, "
            "or reducing INGEST_MAX_CHUNKS and retry."
        ) from exc

    print(
        f"Indexed {len(chunked_documents)} chunks from {len(pdf_paths)} PDF file(s) "
        f"into '{settings.vector_index_dir}'."
    )
