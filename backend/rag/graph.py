"""Lightweight chat pipeline with seams for future LangGraph integration."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from langchain_openai import ChatOpenAI

from backend.config import settings
from backend.rag.classifier import classify_question
from backend.rag.prompts import (
    CAESAR_LIMITATION_PROMPT,
    CAESAR_SYSTEM_PROMPT,
    GUARDRAILS_PROMPT,
    HALLUCINATION_GRADER_PROMPT,
    QUALITY_GRADER_PROMPT,
    QUERY_REWRITE_PROMPT,
    RETRIEVAL_GRADER_PROMPT,
    TOPIC_ROUTER_PROMPT,
)
from backend.rag.retriever import CaesarRetriever, serialize_sources
from backend.rag.types import ChatResult, ClassificationResult, RetrievedSource


@dataclass
class GuardrailsResult:
    passes: bool
    reason: str
    category: str = "safe"


@dataclass
class TopicRoute:
    topic: str
    reason: str


@dataclass
class GradeResult:
    passes: bool
    reason: str
    relevance: float | None = None
    utility: float | None = None


class CaesarChatPipeline:
    """End-to-end chat pipeline for the backend MVP."""

    def __init__(self) -> None:
        self.retriever = CaesarRetriever()

    def run(self, question: str, session_id: str | None = None) -> ChatResult:
        """Classify, retrieve, and answer a user question."""
        guardrails = self._run_guardrails(question)
        if not guardrails.passes:
            return ChatResult(
                question=question,
                answer=(
                    "I will not engage with words that are base or abusive. "
                    "Speak with honor if you would be heard."
                ),
                status="refused_guardrails",
                classification=ClassificationResult(
                    allowed=False,
                    reason=f"Guardrails blocked content: {guardrails.category}.",
                ),
                sources=[],
            )

        topic = self._route_topic(question)
        if topic.topic == "out_of_scope":
            return ChatResult(
                question=question,
                answer=CAESAR_LIMITATION_PROMPT,
                status="refused_out_of_scope",
                classification=ClassificationResult(
                    allowed=False,
                    reason=f"Topic router: {topic.topic}. {topic.reason}",
                ),
                sources=[],
            )
        if topic.topic == "meta":
            return ChatResult(
                question=question,
                answer=(
                    "I speak from my own commentaries and the record of my campaigns. "
                    "Ask of the peoples, battles, or decisions of my age, and I will answer."
                ),
                status="answered_meta",
                classification=ClassificationResult(
                    allowed=True,
                    reason=f"Topic router: {topic.topic}. {topic.reason}",
                ),
                sources=[],
            )
        classification = ClassificationResult(
            allowed=True, reason=f"Topic router: {topic.topic}. {topic.reason}"
        )

        try:
            documents = self._retrieve_with_rewrite(question)
        except (FileNotFoundError, RuntimeError):
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

        graded_documents = self._grade_retrieval(question, documents)
        if not graded_documents and topic.topic == "ambiguous":
            return ChatResult(
                question=question,
                answer=(
                    "Your question is too vague for a sound reply. "
                    "Name the people, place, or event, and I will answer plainly."
                ),
                status="needs_clarification",
                classification=classification,
                sources=[],
            )
        if not graded_documents:
            # Fall back to the ungraded retrieval results rather than failing hard.
            graded_documents = documents

        if not graded_documents:
            return ChatResult(
                question=question,
                answer=(
                    "I find no passage in my writings that answers this plainly. "
                    "Ask again with a matter closer to the campaigns, politics, or peoples I described."
                ),
                status="no_relevant_sources",
                classification=classification,
                sources=[],
            )

        sources = serialize_sources(graded_documents)
        answer, status = self._generate_with_graders(question=question, sources=sources)

        return ChatResult(
            question=question,
            answer=answer,
            status=status,
            classification=classification,
            sources=sources,
        )

    def stream(self, question: str, session_id: str | None = None):
        """Stream a chat response as incremental deltas and a final payload."""
        guardrails = self._run_guardrails(question)
        if not guardrails.passes:
            yield {
                "error": "guardrails_blocked",
                "message": (
                    "I will not engage with words that are base or abusive. "
                    "Speak with honor if you would be heard."
                ),
                "status": "refused_guardrails",
            }
            return

        topic = self._route_topic(question)
        if topic.topic in {"out_of_scope", "meta", "ambiguous"}:
            if topic.topic == "out_of_scope":
                answer = CAESAR_LIMITATION_PROMPT
                status = "refused_out_of_scope"
            elif topic.topic == "meta":
                answer = (
                    "I speak from my own commentaries and the record of my campaigns. "
                    "Ask of the peoples, battles, or decisions of my age, and I will answer."
                )
                status = "answered_meta"
            else:
                answer = (
                    "Your question is too vague for a sound reply. "
                    "Name the people, place, or event, and I will answer plainly."
                )
                status = "needs_clarification"
            yield {
                "done": True,
                "answer": answer,
                "status": status,
                "classifier": {
                    "allowed": topic.topic != "out_of_scope",
                    "reason": f"Topic router: {topic.topic}. {topic.reason}",
                },
                "sources": [],
            }
            return

        classification = ClassificationResult(
            allowed=True, reason=f"Topic router: {topic.topic}. {topic.reason}"
        )

        try:
            documents = self._retrieve_with_rewrite(question)
        except (FileNotFoundError, RuntimeError):
            yield {
                "done": True,
                "answer": (
                    "My library has not yet been prepared for consultation. "
                    "Build the corpus index before seeking an answer from my writings."
                ),
                "status": "index_unavailable",
                "classifier": {
                    "allowed": True,
                    "reason": classification.reason,
                },
                "sources": [],
            }
            return

        graded_documents = self._grade_retrieval(question, documents)
        if not graded_documents:
            graded_documents = documents

        sources = serialize_sources(graded_documents)
        sources_payload = self._serialize_source_payload(sources)
        tangential = self._is_tangential(question, sources)

        if not settings.openai_api_key:
            answer = self._fallback_answer(sources) if sources else (
                "I find no passage in my writings that answers this plainly. "
                "Ask again with a matter closer to the campaigns, politics, or peoples I described."
            )
            yield {
                "done": True,
                "answer": answer,
                "status": "answered" if sources else "no_relevant_sources",
                "classifier": {
                    "allowed": True,
                    "reason": classification.reason,
                },
                "sources": sources_payload,
            }
            return

        full_answer = ""
        for delta in self._stream_answer(
            question=question, sources=sources, tangential=tangential
        ):
            full_answer += delta
            yield {"delta": delta}

        if not tangential:
            full_answer = self._strip_trailing_followup(full_answer)

        yield {
            "done": True,
            "answer": full_answer,
            "status": "answered_partial" if tangential else "answered",
            "classifier": {
                "allowed": True,
                "reason": classification.reason,
            },
            "sources": sources_payload,
        }

    def _run_guardrails(self, question: str) -> GuardrailsResult:
        """Check for inappropriate content before any retrieval or generation."""
        if not settings.openai_api_key:
            lowered = question.lower()
            blocked_terms = [
                "kill",
                "nazi",
                "rape",
                "suicide",
                "genocide",
                "terrorist",
                "bomb",
            ]
            if any(term in lowered for term in blocked_terms):
                return GuardrailsResult(
                    passes=False, reason="Matched blocked term.", category="violence"
                )
            return GuardrailsResult(passes=True, reason="No blocked terms detected.")

        payload = self._invoke_json(
            prompt=f"{GUARDRAILS_PROMPT}\n\nUser message:\n{question}",
            default={"passes": True, "reason": "Default allow.", "category": "safe"},
        )
        return GuardrailsResult(
            passes=bool(payload.get("passes", True)),
            reason=str(payload.get("reason", "")),
            category=str(payload.get("category", "safe")),
        )

    def _route_topic(self, question: str) -> TopicRoute:
        """Classify the topic and decide routing."""
        if not settings.openai_api_key:
            classification = classify_question(question)
            if not classification.allowed:
                return TopicRoute(topic="out_of_scope", reason=classification.reason)
            return TopicRoute(topic="historical", reason=classification.reason)

        payload = self._invoke_json(
            prompt=f"{TOPIC_ROUTER_PROMPT}\n\nQuestion:\n{question}",
            default={"topic": "historical", "reason": "Default to historical."},
        )
        topic = str(payload.get("topic", "historical"))
        if topic not in {"historical", "meta", "out_of_scope", "ambiguous"}:
            topic = "ambiguous"
        return TopicRoute(topic=topic, reason=str(payload.get("reason", "")))

    def _rewrite_queries(self, question: str) -> list[str]:
        """Generate three optimized search queries."""
        if not settings.openai_api_key:
            return [
                question,
                f"Julius Caesar {question}",
                f"Gallic War {question}",
            ]

        payload = self._invoke_json(
            prompt=f"{QUERY_REWRITE_PROMPT}\n\nQuestion:\n{question}",
            default={"queries": [question, question, question]},
        )
        queries = payload.get("queries") or [question, question, question]
        normalized = [str(q).strip() for q in queries if str(q).strip()]
        while len(normalized) < 3:
            normalized.append(question)
        return normalized[:3]

    def _retrieve_with_rewrite(self, question: str) -> list[Any]:
        """Retrieve using query rewrites and union the results."""
        queries = self._rewrite_queries(question)
        union: dict[tuple[Any, ...], Any] = {}

        for query in queries:
            documents = self.retriever.retrieve(query)
            for doc in documents:
                key = (
                    doc.metadata.get("source"),
                    doc.metadata.get("page"),
                    doc.page_content[:120],
                )
                if key not in union:
                    union[key] = doc
                else:
                    existing = union[key]
                    existing_score = existing.metadata.get("score")
                    doc_score = doc.metadata.get("score")
                    if isinstance(existing_score, (int, float)) and isinstance(
                        doc_score, (int, float)
                    ):
                        if doc_score < existing_score:
                            union[key] = doc

        return list(union.values())

    def _grade_retrieval(self, question: str, documents: list[Any]) -> list[Any]:
        """Grade retrieved chunks and keep only the useful ones."""
        if not settings.openai_api_key:
            return documents

        filtered: list[Any] = []
        for doc in documents:
            excerpt = doc.page_content[:800].strip()
            payload = self._invoke_json(
                prompt=(
                    f"{RETRIEVAL_GRADER_PROMPT}\n\nQuestion:\n{question}\n\n"
                    f"Passage:\n{excerpt}"
                ),
                default={
                    "passes": True,
                    "relevance": 1.0,
                    "utility": 1.0,
                    "reason": "Default allow.",
                },
            )
            grade = GradeResult(
                passes=bool(payload.get("passes", False)),
                relevance=float(payload.get("relevance", 0.0) or 0.0),
                utility=float(payload.get("utility", 0.0) or 0.0),
                reason=str(payload.get("reason", "")),
            )
            if (
                grade.passes
                and grade.relevance >= settings.retrieval_relevance_threshold
                and grade.utility >= settings.retrieval_utility_threshold
            ):
                filtered.append(doc)

        return filtered

    def _generate_with_graders(
        self, *, question: str, sources: list[RetrievedSource]
    ) -> tuple[str, str]:
        """Generate an answer with post-hoc graders and retry logic."""
        max_retries = max(0, settings.grader_max_retries)
        tangential = self._is_tangential(question, sources)
        for attempt in range(max_retries + 1):
            answer = self._generate_answer(
                question=question,
                sources=sources,
                retry_index=attempt,
                tangential=tangential,
            )
            if not settings.openai_api_key:
                return answer, "answered"
            if tangential:
                return answer, "answered_partial"

            hallucination = self._invoke_json(
                prompt=(
                    f"{HALLUCINATION_GRADER_PROMPT}\n\nQuestion:\n{question}\n\n"
                    f"Answer:\n{answer}\n\nSources:\n{self._format_sources(sources)}"
                ),
                default={"passes": True, "reason": "Default allow."},
            )
            if not bool(hallucination.get("passes", False)):
                if attempt < max_retries:
                    continue
                return (
                    (
                        f"{answer}\n\nIs this the matter you meant?"
                        if tangential
                        else answer
                    ),
                    "failed_hallucination",
                )

            quality = self._invoke_json(
                prompt=(
                    f"{QUALITY_GRADER_PROMPT}\n\nQuestion:\n{question}\n\n"
                    f"Answer:\n{answer}"
                ),
                default={"passes": True, "reason": "Default allow."},
            )
            if not bool(quality.get("passes", False)):
                if attempt < max_retries:
                    continue
                return (
                    (
                        f"{answer}\n\nIs this the matter you meant?"
                        if tangential
                        else answer
                    ),
                    "failed_quality",
                )

            return answer, "answered"

        return (
            f"{answer}\n\nIs this the matter you meant?" if tangential else answer,
            "failed_generation",
        )

    def _generate_answer(
        self,
        question: str,
        sources: list[RetrievedSource],
        retry_index: int = 0,
        tangential: bool = False,
    ) -> str:
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
        context = self._format_sources(sources)
        retry_note = ""
        if retry_index > 0:
            retry_note = (
                "\n\nDouble-check grounding: only include claims supported by the sources. "
                "If support is unclear, say so plainly."
            )
        tangential_note = ""
        if tangential:
            tangential_note = (
                "\n\nThe sources are only tangentially related. "
                "Give the best partial answer you can and end with a short clarifying question. "
                "If not tangential, do not ask a follow-up question."
            )
        prompt = (
            f"{CAESAR_SYSTEM_PROMPT}\n\n"
            f"Question: {question}\n\n"
            f"Retrieved context:\n{context}\n\n"
            "Answer in first-person present tense as Caesar using only the retrieved material. "
            "Paraphrase and synthesize; do not quote unless explicitly requested."
            f"{tangential_note}"
            f"{retry_note}"
        )
        response = llm.invoke(prompt)
        content = response.content.strip()
        if not tangential:
            return self._strip_trailing_followup(content)
        return content

    def _stream_answer(
        self, *, question: str, sources: list[RetrievedSource], tangential: bool
    ):
        """Stream answer tokens from the LLM."""
        llm = ChatOpenAI(
            model=settings.openai_chat_model,
            api_key=settings.openai_api_key,
            temperature=0.2,
        )
        context = self._format_sources(sources)
        tangential_note = ""
        if tangential:
            tangential_note = (
                "\n\nThe sources are only tangentially related. "
                "Give the best partial answer you can and end with a short clarifying question. "
                "If not tangential, do not ask a follow-up question."
            )
        prompt = (
            f"{CAESAR_SYSTEM_PROMPT}\n\n"
            f"Question: {question}\n\n"
            f"Retrieved context:\n{context}\n\n"
            "Answer in first-person present tense as Caesar using only the retrieved material. "
            "Paraphrase and synthesize; do not quote unless explicitly requested."
            f"{tangential_note}"
        )
        for chunk in llm.stream(prompt):
            if chunk.content:
                yield chunk.content

    def _format_sources(self, sources: list[RetrievedSource]) -> str:
        return "\n\n".join(
            f"Source: {source.source} (page {source.page})\n{source.excerpt}"
            for source in sources
        )

    @staticmethod
    def _serialize_source_payload(sources: list[RetrievedSource]) -> list[dict]:
        return [
            {
                "source": source.source,
                "page": source.page,
                "excerpt": source.excerpt,
                "score": source.score,
            }
            for source in sources
        ]

    @staticmethod
    def _strip_trailing_followup(text: str) -> str:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return text
        last = lines[-1]
        followup_markers = (
            "would you like",
            "is this",
            "do you wish",
            "shall i",
            "do you want",
            "would you wish",
        )
        if last.endswith("?") and any(marker in last.lower() for marker in followup_markers):
            lines = lines[:-1]
        return "\n\n".join(lines).strip()

    @staticmethod
    def _is_tangential(question: str, sources: list[RetrievedSource]) -> bool:
        """Heuristic: treat broad questions with weak lexical overlap as tangential."""
        if not sources:
            return False
        lowered_question = question.lower()
        key_terms = [term for term in ("rome", "roman", "senate", "city", "war", "warfare", "battle") if term in lowered_question]
        if not key_terms:
            return False
        combined = " ".join(source.excerpt.lower() for source in sources)
        return not any(term in combined for term in key_terms)

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

    def _invoke_json(self, *, prompt: str, default: dict[str, Any]) -> dict[str, Any]:
        if not settings.openai_api_key:
            return default
        llm = ChatOpenAI(
            model=settings.openai_chat_model,
            api_key=settings.openai_api_key,
            temperature=0.0,
        )
        response = llm.invoke(prompt)
        content = response.content.strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(content[start : end + 1])
                except json.JSONDecodeError:
                    return default
        return default
