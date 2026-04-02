"""CLI entrypoint for building the local FAISS corpus index."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.rag.ingest import ingest_corpus


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ingest Caesar PDFs into a local FAISS index."
    )
    parser.add_argument(
        "--max-pages-per-pdf",
        type=int,
        default=None,
        help="Limit pages processed per PDF (defaults to INGEST_MAX_PAGES_PER_PDF).",
    )
    parser.add_argument(
        "--max-chunks",
        type=int,
        default=None,
        help="Limit total chunks embedded (defaults to INGEST_MAX_CHUNKS).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Embedding batch size (defaults to INGEST_BATCH_SIZE).",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=None,
        help="Sleep between batches (defaults to INGEST_SLEEP_SECONDS).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Estimate tokens and cost without embedding or indexing.",
    )

    args = parser.parse_args()
    ingest_corpus(
        max_pages_per_pdf=args.max_pages_per_pdf,
        max_chunks=args.max_chunks,
        batch_size=args.batch_size,
        sleep_seconds=args.sleep_seconds,
        dry_run=args.dry_run,
    )
