from __future__ import annotations

from typing import Any

from core.constants.reranker import (
    ALPHA,
    BETA,
    S1_ALPHA,
    S1_BETA,
    S3_PLACEHOLDER,
    TOP_K,
)
from core.entities.scored_chunk import ScoredChunk


def _build_provenance(c: ScoredChunk) -> dict[str, Any]:
    s1_formula = (
        f"0.4*{c.bm25_norm:.4f} + 0.6*{c.vector_norm:.4f}"
    )
    return {
        "id": c.id,
        "retrieval_source": c.retrieval_source,
        "bm25_score": round(c.bm25_score, 4),
        "vector_score": round(c.vector_score, 4),
        "bm25_norm": round(c.bm25_norm, 4),
        "vector_norm": round(c.vector_norm, 4),
        "s1_formula": s1_formula,
        "s1": round(c.s1, 4),
        "distance": c.distance,
        "s2": round(c.s2, 4),
        "s2_formula": f"1/(1+{c.distance})",
        "final_score": round(c.final_score, 4),
        "final_formula": f"0.8*{c.s1:.4f} + 0.2*{c.s2:.4f}",
        "content": (c.content[:200] + "...") if len(c.content) > 200 else c.content,
    }


def min_max_normalize(values: list[float]) -> list[float]:
    if not values:
        return []
    mn = min(values)
    mx = max(values)
    if mx - mn < 1e-12:
        return [1.0] * len(values)
    return [(v - mn) / (mx - mn) for v in values]


def normalize_scores(chunks: list[ScoredChunk]) -> list[ScoredChunk]:
    bm25_vals = [c.bm25_score for c in chunks]
    vec_vals = [c.vector_score for c in chunks]
    bm25_norms = min_max_normalize(bm25_vals)
    vec_norms = min_max_normalize(vec_vals)
    for c, bn, vn in zip(chunks, bm25_norms, vec_norms):
        c.bm25_norm = bn
        c.vector_norm = vn
    return chunks


def compute_s1(
    bm25_norm: float,
    vector_norm: float,
    alpha: float = S1_ALPHA,
    beta: float = S1_BETA,
) -> float:
    return alpha * bm25_norm + beta * vector_norm


def compute_s2(distance: int) -> float:
    return 1.0 / (1.0 + distance)


def compute_final(
    s1: float,
    s2: float,
    s3: float = S3_PLACEHOLDER,
    alpha: float = ALPHA,
    beta: float = BETA,
) -> float:
    return alpha * s1 + beta * s2 + 0.0 * s3


class Reranker:
    def __init__(
        self,
        top_k: int = TOP_K,
        alpha: float = ALPHA,
        beta: float = BETA,
    ) -> None:
        self._top_k = top_k
        self._alpha = alpha
        self._beta = beta

    def rerank(self, chunks: list[ScoredChunk]) -> list[ScoredChunk]:
        for c in chunks:
            c.final_score = compute_final(
                c.s1, c.s2, alpha=self._alpha, beta=self._beta
            )
            c.provenance = _build_provenance(c)

        chunks.sort(key=lambda c: c.final_score, reverse=True)
        return chunks[: self._top_k]
