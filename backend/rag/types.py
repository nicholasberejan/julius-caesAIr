"""Shared types for the MVP RAG pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ClassificationResult:
    """Outcome of the Caesar plausibility classifier."""

    allowed: bool
    reason: str


@dataclass
class RetrievedSource:
    """Serializable source reference."""

    source: str
    page: int | None
    excerpt: str
    score: float | None = None


@dataclass
class ChatResult:
    """End-to-end chat pipeline output."""

    question: str
    answer: str
    status: str
    classification: ClassificationResult
    sources: list[RetrievedSource] = field(default_factory=list)
