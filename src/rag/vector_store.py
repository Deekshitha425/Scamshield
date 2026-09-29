"""
Vector store wrapper around ChromaDB, used as the Threat-Intel RAG corpus.
Keeps embedding logic in one place so agents never touch ChromaDB directly.

Heavy dependencies (sentence-transformers/torch) are imported lazily inside
__init__ rather than at module level, so unit tests for agent logic that
don't actually touch retrieval (e.g. tests/test_judge_agent.py's mocked
scenarios) don't require the full ML stack to be installed.
"""
from __future__ import annotations
import chromadb
from src.config import settings

_COLLECTION_NAME = "threat_intel_corpus"


class VectorStore:
    def __init__(self):
        from sentence_transformers import SentenceTransformer  # lazy import

        self._client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self._collection = self._client.get_or_create_collection(_COLLECTION_NAME)
        self._embedder = SentenceTransformer(settings.embedding_model)

    def add_documents(self, docs: list[str], ids: list[str], metadatas: list[dict] | None = None):
        embeddings = self._embedder.encode(docs).tolist()
        self._collection.add(
            documents=docs, embeddings=embeddings, ids=ids, metadatas=metadatas or [{}] * len(docs)
        )

    def query(self, text: str, top_k: int = 3) -> list[tuple[str, float, dict]]:
        """Returns (document, similarity_score, metadata) tuples, best first."""
        embedding = self._embedder.encode([text]).tolist()
        results = self._collection.query(query_embeddings=embedding, n_results=top_k)
        docs = results["documents"][0] if results["documents"] else []
        distances = results["distances"][0] if results["distances"] else []
        metadatas = results["metadatas"][0] if results["metadatas"] else []
        # ChromaDB returns distance (lower = closer); convert to a similarity score.
        similarities = [max(0.0, 1.0 - d) for d in distances]
        return list(zip(docs, similarities, metadatas))
