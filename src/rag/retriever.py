"""
Retriever — the interface the Judge calls when it decides more evidence is
needed. Wraps VectorStore so the sufficiency-gating logic in judge_agent.py
doesn't need to know embedding details.
"""
from __future__ import annotations
from src.agents.schemas import RetrievedExample
from src.rag.vector_store import VectorStore

_store: VectorStore | None = None


def get_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
    return _store


def retrieve_similar_scams(query_text: str, top_k: int = 3) -> list[RetrievedExample]:
    results = get_store().query(query_text, top_k=top_k)
    return [
        RetrievedExample(
            text=doc,
            similarity=score,
            source=meta.get("source", "unknown"),
            label=meta.get("label", "scam"),
        )
        for doc, score, meta in results
    ]