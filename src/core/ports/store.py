from __future__ import annotations

from typing import Any, Optional, Protocol


class DocumentStore(Protocol):
    def search_bm25(self, query: str, rows: int = 20, fl: str = "*,score") -> list[dict[str, Any]]:
        ...

    def search_vector(self, vector: list[float], rows: int = 20, fl: str = "*,score") -> list[dict[str, Any]]:
        ...

    def get_by_id(self, doc_id: str) -> Optional[dict[str, Any]]:
        ...

    def index_documents(self, docs: list[dict[str, Any]]) -> None:
        ...

    def delete_all(self) -> None:
        ...

    def commit(self) -> None:
        ...

    def close(self) -> None:
        ...
