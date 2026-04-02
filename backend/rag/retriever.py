"""Retriever helpers for the Caesar corpus."""

from __future__ import annotations

from langchain_core.documents import Document

from backend.config import settings
from backend.rag.embeddings import load_faiss_index
from backend.rag.types import RetrievedSource


class CaesarRetriever:
    """Thin wrapper around the local FAISS retriever."""

    def __init__(self) -> None:
        self._vectorstore = None

    @property
    def vectorstore(self):
        """Lazily load the vector store."""
        if self._vectorstore is None:
            self._vectorstore = load_faiss_index(settings.vector_index_dir)
        return self._vectorstore

    def retrieve(self, question: str, top_k: int | None = None) -> list[Document]:
        """Retrieve relevant documents for a user question."""
        k = top_k or settings.default_top_k
        try:
            results = self.vectorstore.similarity_search_with_score(question, k=k)
        except AttributeError:
            return self.vectorstore.similarity_search(question, k=k)

        documents: list[Document] = []
        for doc, score in results:
            doc.metadata = dict(doc.metadata)
            doc.metadata["score"] = float(score)
            documents.append(doc)
        return documents


def serialize_sources(documents: list[Document]) -> list[RetrievedSource]:
    """Convert LangChain documents into API-friendly source objects."""
    serialized: list[RetrievedSource] = []
    for doc in documents:
        excerpt = doc.page_content[:280].strip()
        serialized.append(
            RetrievedSource(
                source=str(doc.metadata.get("source", "unknown")),
                page=doc.metadata.get("page"),
                excerpt=excerpt,
                score=doc.metadata.get("score"),
            )
        )
    return serialized
