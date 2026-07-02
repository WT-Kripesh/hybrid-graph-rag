from __future__ import annotations

from typing import Optional

from core.entities.scored_chunk import ScoredChunk
from rag.reranker.reranker import compute_s2
from core.ports.store import DocumentStore

MAX_DEPTH = 2


class HierarchyExpander:
    def __init__(self, store: DocumentStore) -> None:
        self._store = store

    def expand(
        self,
        chunks: list[ScoredChunk],
        max_depth: int = MAX_DEPTH,
    ) -> list[ScoredChunk]:
        seen: dict[str, ScoredChunk] = {}

        for c in chunks:
            seen[c.id] = c

        for c in chunks:
            parent_id: Optional[str] = c.parent_id
            distance = 1
            while parent_id and distance <= max_depth:
                if parent_id in seen:
                    parent_id = seen[parent_id].parent_id
                    distance += 1
                    continue
                doc = self._store.get_by_id(parent_id)
                if doc is None:
                    break
                ancestor = ScoredChunk(
                    id=doc.get("id", ""),
                    doc_id=doc.get("doc_id", ""),
                    node_type=doc.get("node_type", ""),
                    title=doc.get("title", ""),
                    content=doc.get("content", ""),
                    section_path=doc.get("section_path", ""),
                    level=int(doc.get("level", 0)),
                    parent_id=doc.get("parent_id"),
                    embedding=doc.get("embedding"),
                    retrieval_source="ancestor",
                    distance=distance,
                    s2=compute_s2(distance),
                )
                seen[ancestor.id] = ancestor
                parent_id = ancestor.parent_id
                distance += 1

        expanded = list(seen.values())
        for c in expanded:
            c.s2 = compute_s2(c.distance)
        return expanded
