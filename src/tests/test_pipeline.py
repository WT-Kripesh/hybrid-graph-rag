"""End-to-end integration tests for the full RAG pipeline.

These tests require:
- LM Studio running on localhost:1234 with an embedding model
- Solr 9.x running on localhost:8983 with the hybrid_rag collection

Run with:
    uv run python -m pytest src/tests/test_pipeline.py -v
"""

from __future__ import annotations

import pytest

from adapters.lm_studio.embedder import LMStudioEmbedder
from adapters.solr.client import SolrClient
from adapters.solr.store import SolrDocumentStore

from rag.retrieval.hybrid import HybridRetriever
from rag.retrieval.hierarchy import HierarchyExpander
from rag.reranker.reranker import Reranker
from rag.generation.context import ContextBuilder


@pytest.fixture
def solr() -> SolrClient:
    client = SolrClient()
    yield client
    client.close()


@pytest.fixture
def store(solr: SolrClient) -> SolrDocumentStore:
    return SolrDocumentStore(solr)


@pytest.fixture
def embedder() -> LMStudioEmbedder:
    return LMStudioEmbedder()


def test_hybrid_retriever(store: SolrDocumentStore) -> None:
    import numpy as np

    retriever = HybridRetriever(store)
    results = retriever.retrieve("payment terms", np.zeros(768).tolist(), top_k=5)
    assert isinstance(results, list)


def test_hierarchy_expander(sample_md_content: str, store: SolrDocumentStore) -> None:
    import numpy as np

    retriever = HybridRetriever(store)
    expander = HierarchyExpander(store)
    results = retriever.retrieve("terms", np.zeros(768).tolist(), top_k=5)
    expanded = expander.expand(results)
    assert len(expanded) >= len(results)


def test_reranker_sorts_by_final_score(store: SolrDocumentStore) -> None:
    import numpy as np

    retriever = HybridRetriever(store)
    expander = HierarchyExpander(store)
    reranker = Reranker(top_k=5)
    results = retriever.retrieve("payment terms", np.zeros(768).tolist(), top_k=10)
    expanded = expander.expand(results)
    reranked = reranker.rerank(expanded)
    assert len(reranked) <= 5
    for i in range(len(reranked) - 1):
        assert reranked[i].final_score >= reranked[i + 1].final_score


def test_reranker_adds_provenance(store: SolrDocumentStore) -> None:
    import numpy as np

    retriever = HybridRetriever(store)
    expander = HierarchyExpander(store)
    reranker = Reranker(top_k=5)
    results = retriever.retrieve("payment terms", np.zeros(768).tolist(), top_k=5)
    expanded = expander.expand(results)
    reranked = reranker.rerank(expanded)
    for c in reranked:
        assert "s1" in c.provenance
        assert "s2" in c.provenance
        assert "final_score" in c.provenance


@pytest.mark.asyncio
async def test_context_builder_builds_string(store: SolrDocumentStore) -> None:
    import numpy as np

    retriever = HybridRetriever(store)
    expander = HierarchyExpander(store)
    reranker = Reranker(top_k=3)
    builder = ContextBuilder()
    results = retriever.retrieve("payment terms", np.zeros(768).tolist(), top_k=5)
    expanded = expander.expand(results)
    reranked = reranker.rerank(expanded)
    context = builder.build(reranked)
    assert isinstance(context, str)
    assert len(context) > 0
