from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ScoredChunk:
    id: str
    doc_id: str
    node_type: str
    title: str
    content: str
    section_path: str
    level: int
    parent_id: Optional[str]
    embedding: Optional[list[float]]
    bm25_score: float = 0.0
    vector_score: float = 0.0
    s1: float = 0.0
    s2: float = 0.0
    final_score: float = 0.0
    retrieval_source: str = "bm25"
    distance: int = 0
    bm25_norm: float = 0.0
    vector_norm: float = 0.0
    provenance: dict[str, Any] = field(default_factory=dict)
