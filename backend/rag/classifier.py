"""Heuristic classifier for whether Caesar could plausibly answer a question."""

from __future__ import annotations

import re

from backend.rag.types import ClassificationResult


MODERN_CONCEPT_PATTERNS = [
    r"\bcomputer\b",
    r"\binternet\b",
    r"\bsmartphone\b",
    r"\bemail\b",
    r"\bbitcoin\b",
    r"\bai\b",
    r"\bartificial intelligence\b",
    r"\bmachine learning\b",
    r"\bquantum\b",
    r"\bprogramming\b",
    r"\bsoftware\b",
    r"\bdemocracy\b",
    r"\bunited states\b",
    r"\bworld war\b",
    r"\bnuclear\b",
    r"\brocket\b",
    r"\bautomobile\b",
    r"\bairplane\b",
]


def classify_question(question: str) -> ClassificationResult:
    """Return whether the question is plausibly within Caesar's worldview."""
    normalized = question.strip().lower()
    if not normalized:
        return ClassificationResult(
            allowed=False,
            reason="The question was empty.",
        )

    for pattern in MODERN_CONCEPT_PATTERNS:
        if re.search(pattern, normalized):
            return ClassificationResult(
                allowed=False,
                reason="The question depends on concepts outside Caesar's historical world.",
            )

    return ClassificationResult(
        allowed=True,
        reason="The question appears historically plausible for Caesar to address.",
    )
