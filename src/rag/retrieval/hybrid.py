from __future__ import annotations

from typing import Any

from core.constants.reranker import TOP_K
from core.entities.scored_chunk import ScoredChunk
from rag.reranker.reranker import compute_s1, normalize_scores
from core.ports.store import DocumentStore


def _solr_to_scored(
    doc: dict[str, Any],
    source: str,
    bm25_score: float = 0.0,
    vector_score: float = 0.0,
) -> ScoredChunk:
    return ScoredChunk(
        id=doc.get("id", ""),
        doc_id=doc.get("doc_id", ""),
        node_type=doc.get("node_type", ""),
        title=doc.get("title", ""),
        content=doc.get("content", ""),
        section_path=doc.get("section_path", ""),
        level=int(doc.get("level", 0)),
        parent_id=doc.get("parent_id"),
        embedding=doc.get("embedding"),
        bm25_score=bm25_score,
        vector_score=vector_score,
        retrieval_source=source,
    )


class HybridRetriever:
    def __init__(self, store: DocumentStore) -> None:
        self._store = store

    def retrieve(
        self,
        query: str,
        query_vector: list[float],
        top_k: int = TOP_K,
    ) -> list[ScoredChunk]:
        bm25_docs = self._store.search_bm25(query, rows=top_k)
        vector_docs = self._store.search_vector(query_vector, rows=top_k)

        seen: dict[str, ScoredChunk] = {}

        for d in bm25_docs:
            doc_id = d.get("id", "")
            raw_score = float(d.get("score", 0.0))
            seen[doc_id] = _solr_to_scored(
                d, "bm25", bm25_score=raw_score, vector_score=0.0
            )

        for d in vector_docs:
            doc_id = d.get("id", "")
            raw_score = float(d.get("score", 0.0))
            if doc_id in seen:
                existing = seen[doc_id]
                existing.vector_score = raw_score
                existing.retrieval_source = "bm25"
            else:
                seen[doc_id] = _solr_to_scored(
                    d, "vector", bm25_score=0.0, vector_score=raw_score
                )

        chunks = list(seen.values())
        chunks = normalize_scores(chunks)

        for c in chunks:
            c.s1 = compute_s1(c.bm25_norm, c.vector_norm)

        return chunks
