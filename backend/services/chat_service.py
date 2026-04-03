"""Service wrapper around the RAG chat pipeline."""

from __future__ import annotations

from backend.rag.graph import CaesarChatPipeline


class ChatService:
    """Application-facing chat service."""

    def __init__(self) -> None:
        self.pipeline = CaesarChatPipeline()

    def reply(self, message: str, session_id: str | None = None) -> dict:
        """Generate a chat response payload."""
        result = self.pipeline.run(question=message, session_id=session_id)
        return {
            "session_id": session_id,
            "question": result.question,
            "answer": result.answer,
            "status": result.status,
            "classifier": {
                "allowed": result.classification.allowed,
                "reason": result.classification.reason,
            },
            "sources": [
                {
                    "source": source.source,
                    "page": source.page,
                    "excerpt": source.excerpt,
                    "score": source.score,
                }
                for source in result.sources
            ],
        }

    def stream_reply(self, message: str, session_id: str | None = None):
        """Stream a chat response payload as incremental events."""
        return self.pipeline.stream(question=message, session_id=session_id)
