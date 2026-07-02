from __future__ import annotations

import pytest

from chunker.tree_builder import chunk_markdown, chunk_plain_text
from adapters.lm_studio.embedder import LMStudioEmbedder


@pytest.mark.asyncio
async def test_chunk_markdown_document(sample_md_content: str) -> None:
    embedder = LMStudioEmbedder()
    root = await chunk_markdown(
        sample_md_content,
        doc_title="test",
        organization="org-test",
        embedder=embedder,
    )
    counts = root.count_by_type()
    assert counts["document"] == 1
    assert counts["section"] >= 2
    assert counts["chunk"] >= 1
    assert root.title == "test"

    docs = root.flatten()
    assert len(docs) > 0
    for doc in docs:
        assert "id" in doc
        assert "node_type" in doc
        assert "title" in doc
        assert "section_path" in doc


@pytest.mark.asyncio
async def test_chunk_plain_text_document(sample_txt_content: str) -> None:
    embedder = LMStudioEmbedder()
    root = await chunk_plain_text(
        sample_txt_content,
        doc_title="test",
        organization="org-test",
        embedder=embedder,
    )
    counts = root.count_by_type()
    assert counts["document"] == 1
    assert counts["chunk"] >= 1

    docs = root.flatten()
    assert len(docs) > 0
    for doc in docs:
        assert doc["document_style"] == "flat"


@pytest.mark.asyncio
async def test_chunk_with_fixed_size_strategy(sample_md_content: str) -> None:
    embedder = LMStudioEmbedder()
    from chunker.fixed_size import FixedSizeChunker
    strategy = FixedSizeChunker(chunk_size=50, overlap=5)
    root = await chunk_markdown(
        sample_md_content,
        doc_title="test",
        organization="org-test",
        embedder=embedder,
        strategy=strategy,
    )
    counts = root.count_by_type()
    assert counts["document"] == 1
    assert counts["chunk"] >= 1
