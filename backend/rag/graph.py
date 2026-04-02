"""Lightweight chat pipeline with seams for future LangGraph integration."""

from __future__ import annotations

from langchain_openai import ChatOpenAI

from backend.config import settings
from backend.rag.classifier import classify_question
from backend.rag.prompts import CAESAR_LIMITATION_PROMPT, CAESAR_SYSTEM_PROMPT
from backend.rag.retriever import CaesarRetriever, serialize_sources
from backend.rag.types import ChatResult, RetrievedSource


class CaesarChatPipeline:
    """End-to-end chat pipeline for the backend MVP."""

    def __init__(self) -> None:
        self.retriever = CaesarRetriever()

    def run(self, question: str, session_id: str | None = None) -> ChatResult:
        """Classify, retrieve, and answer a user question."""
        classification = classify_question(question)
        if not classification.allowed:
            return ChatResult(
                question=question,
                answer=CAESAR_LIMITATION_PROMPT,
                status="refused_out_of_scope",
                classification=classification,
                sources=[],
            )

        try:
            documents = self.retriever.retrieve(question)
        except (FileNotFoundError, RuntimeError) as exc:
            return ChatResult(
                question=question,
                answer=(
                    "My library has not yet been prepared for consultation. "
                    "Build the corpus index before seeking an answer from my writings."
                ),
                status="index_unavailable",
                classification=classification,
                sources=[],
            )

        sources = serialize_sources(documents)
        answer = self._generate_answer(question=question, sources=sources)

        return ChatResult(
            question=question,
            answer=answer,
            status="answered",
            classification=classification,
            sources=sources,
        )

    def _generate_answer(self, question: str, sources: list[RetrievedSource]) -> str:
        """Generate an answer using the configured LLM or a retrieval fallback."""
        if not sources:
            return (
                "I find no passage in my writings that answers this plainly. "
                "Ask again with a matter closer to the campaigns, politics, or peoples I described."
            )

        if not settings.openai_api_key:
            return self._fallback_answer(sources)

        llm = ChatOpenAI(
            model=settings.openai_chat_model,
            api_key=settings.openai_api_key,
            temperature=0.2,
        )
        context = "\n\n".join(
            f"Source: {source.source} (page {source.page})\n{source.excerpt}"
            for source in sources
        )
        prompt = (
            f"{CAESAR_SYSTEM_PROMPT}\n\n"
            f"Question: {question}\n\n"
            f"Retrieved context:\n{context}\n\n"
            "Answer in first-person present tense as Caesar using only the retrieved material. "
            "Paraphrase and synthesize; do not quote unless explicitly requested."
        )
        response = llm.invoke(prompt)
        return response.content.strip()

    @staticmethod
    def _fallback_answer(sources: list[RetrievedSource]) -> str:
        """Return a non-LLM fallback so the app still behaves coherently."""
        lead = sources[0]
        return (
            "From the passages at hand, I would answer only with caution. "
            f"The nearest evidence comes from {lead.source}"
            f"{f', page {lead.page}' if lead.page else ''}: "
            f"\"{lead.excerpt}\""
        )
