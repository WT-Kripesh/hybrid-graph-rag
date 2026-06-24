from __future__ import annotations

import os
from typing import Any

from chunker.tree_builder import chunk_markdown, chunk_plain_text
from core.ports.embedder import Embedder
from core.ports.store import DocumentStore


def _detect_style(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return "markdown" if ext == ".md" else "flat"


def _doc_title(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]


async def ingest_document(
    input_path: str,
    embedder: Embedder,
    store: DocumentStore,
    organization: str = "org-default",
    style: str = "auto",
    delete_first: bool = False,
) -> dict[str, int]:
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    style = _detect_style(input_path) if style == "auto" else style

    with open(input_path, "r", encoding="utf-8") as fh:
        text = fh.read()

    title = _doc_title(input_path)

    if style == "markdown":
        root = await chunk_markdown(
            text,
            doc_title=title,
            organization=organization,
            embedder=embedder,
        )
    else:
        root = await chunk_plain_text(
            text,
            doc_title=title,
            organization=organization,
            embedder=embedder,
        )

    docs: list[dict[str, Any]] = root.flatten()

    if delete_first:
        store.delete_all()

    store.index_documents(docs)
    store.commit()

    return root.count_by_type()
