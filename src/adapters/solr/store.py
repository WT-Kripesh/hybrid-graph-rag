from __future__ import annotations

from typing import Any, Optional

from adapters.solr.client import SolrClient


class SolrDocumentStore:
    def __init__(self, solr: SolrClient) -> None:
        self._solr = solr

    def search_bm25(self, query: str, rows: int = 20, fl: str = "*,score") -> list[dict[str, Any]]:
        return self._solr.search_bm25(query, rows, fl)

    def search_vector(self, vector: list[float], rows: int = 20, fl: str = "*,score") -> list[dict[str, Any]]:
        return self._solr.search_vector(vector, rows, fl)

    def get_by_id(self, doc_id: str) -> Optional[dict[str, Any]]:
        return self._solr.get_by_id(doc_id)

    def index_documents(self, docs: list[dict[str, Any]]) -> None:
        self._solr.index_documents(docs)

    def delete_all(self) -> None:
        self._solr.delete_all()

    def commit(self) -> None:
        self._solr.commit()

    def close(self) -> None:
        self._solr.close()
