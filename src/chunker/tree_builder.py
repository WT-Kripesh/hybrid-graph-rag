from __future__ import annotations

import re
import uuid
from dataclasses import replace
from typing import Any

from core.constants.chunker import (
    CHUNK_PATH_PREFIX,
    DEFAULT_SLUG,
    DEFAULT_UNTITLED_DOCUMENT_TITLE,
    DOCUMENT_LEVEL,
    PART_TITLE_SEPARATOR,
    PATH_SEPARATOR,
    SLUG_PATTERN,
    SLUG_SEPARATOR,
)
from core.entities.chunk_node import ChunkNode, DocumentStyle, NodeType
from core.entities.document import MarkdownSection

from core.ports.embedder import Embedder
from core.ports.chunker import BaseChunker
from chunker.semantic_splitter import SemanticChunker, segment_sentences
from chunker.markdown_parser import parse_markdown_outline, split_paragraphs
from core.tail_call import AsyncTailCall, async_tail_call_optimized

_SLUG_RE = re.compile(SLUG_PATTERN)


def slugify(text: str) -> str:
    return (
        _SLUG_RE.sub(SLUG_SEPARATOR, text.lower().strip()).strip(SLUG_SEPARATOR)
        or DEFAULT_SLUG
    )


def _join_path(prefix: str, slug: str) -> str:
    return slug if not prefix else f"{prefix}{PATH_SEPARATOR}{slug}"


def _chunk_path(section_path: str, i: int) -> str:
    return f"{section_path}{PATH_SEPARATOR}{CHUNK_PATH_PREFIX}{i}"


def _chunk_title(title: str, i: int, multi: bool) -> str:
    return f"{title}{PART_TITLE_SEPARATOR}{i + 1}" if multi else title


def _fmt_coherence_score(score: float | None) -> str | None:
    return f"{score:.2f}" if score is not None else None


async def _build_chunks(
    section: MarkdownSection,
    embedder: Embedder,
    doc_id: str,
    section_path: str,
    parent_id: str,
    level: int,
    strategy: BaseChunker,
    document_style: DocumentStyle = DocumentStyle.STRUCTURED,
) -> list[ChunkNode]:
    if not section.content.strip():
        return []
    text_chunks = await strategy.chunk(section.content, embedder)
    if not text_chunks:
        return []
    chunk_embeddings = await embedder.embed(
        [chunk.text for chunk in text_chunks]
    )
    has_multiple_chunks = len(text_chunks) > 1
    return [
        ChunkNode(
            id=str(uuid.uuid4()),
            doc_id=doc_id,
            node_type=NodeType.CHUNK,
            title=_chunk_title(section.title, i, has_multiple_chunks),
            content=chunk.text,
            level=level,
            section_path=_chunk_path(section_path, i),
            embedding=embedding,
            chunk_order=i,
            chunk_group_id=i,
            group_coherence_score=_fmt_coherence_score(chunk.coherence_score),
            parent_id=parent_id,
            document_style=document_style,
        )
        for i, (chunk, embedding) in enumerate(
            zip(text_chunks, chunk_embeddings)
        )
    ]


_FRAME_WAIT = "wait"
_FRAME_SECTION = "section"
_FRAME_NODE = "node"


async def _build_step(
    pending: list[tuple],
    done: list[ChunkNode],
    embedder: Embedder,
    strategy: BaseChunker,
) -> Any:
    if not pending:
        return done

    frame = pending[0]
    rest = pending[1:]

    if frame[0] == _FRAME_NODE:
        return AsyncTailCall(
            lambda: _build_step(rest, [*done, frame[1]], embedder, strategy)
        )

    if frame[0] == _FRAME_SECTION:
        _, section, section_path, parent_id, doc_id, org = frame
        child_frames = [
            (
                _FRAME_SECTION,
                child,
                _join_path(section_path, slugify(child.title)),
                None,
                doc_id,
                org,
            )
            for child in section.children
        ]
        wait_frame = (
            _FRAME_WAIT,
            len(section.children),
            section,
            section_path,
            parent_id,
            doc_id,
            org,
        )
        return AsyncTailCall(
            lambda: _build_step(
                [*child_frames, wait_frame, *rest], done, embedder, strategy
            )
        )

    _, n_children, section, section_path, parent_id, doc_id, org = frame
    child_nodes, earlier = (
        done[-n_children:] if n_children else [],
        done[:-n_children] if n_children else done,
    )

    node_id = str(uuid.uuid4())
    node_type = (
        NodeType.DOCUMENT
        if section.level == DOCUMENT_LEVEL
        else NodeType.SECTION
    )
    chunk_children = await _build_chunks(
        section,
        embedder,
        doc_id,
        section_path,
        node_id,
        section.level + 1,
        strategy,
    )

    wired_children = chunk_children + [
        replace(child_node, parent_id=node_id, doc_id=doc_id)
        for child_node in child_nodes
    ]

    node = ChunkNode(
        id=node_id,
        doc_id=doc_id,
        node_type=node_type,
        title=section.title,
        level=section.level,
        section_path=section_path,
        organization=org,
        children=wired_children,
    )
    return AsyncTailCall(
        lambda: _build_step(rest, [*earlier, node], embedder, strategy)
    )


_build_step_tree = async_tail_call_optimized(_build_step)


async def _build_node(
    root_section: MarkdownSection,
    embedder: Embedder,
    doc_id: str,
    organization: str | None,
    doc_slug: str,
    strategy: BaseChunker,
) -> ChunkNode:
    initial = [
        (_FRAME_SECTION, root_section, doc_slug, None, doc_id, organization)
    ]
    result = await _build_step_tree(initial, [], embedder, strategy)
    return result[0]


async def chunk_markdown(
    markdown_text: str,
    doc_title: str = DEFAULT_UNTITLED_DOCUMENT_TITLE,
    organization: str | None = None,
    doc_id: str | None = None,
    embedder: Embedder | None = None,
    strategy: BaseChunker | None = None,
) -> ChunkNode:
    from adapters.lm_studio.embedder import LMStudioEmbedder

    embedder = embedder or LMStudioEmbedder()
    doc_id = doc_id or str(uuid.uuid4())
    strategy = strategy or SemanticChunker(split_fn=segment_sentences)
    outline = replace(parse_markdown_outline(markdown_text), title=doc_title)
    return await _build_node(
        outline, embedder, doc_id, organization, slugify(doc_title), strategy
    )


async def chunk_plain_text(
    text: str,
    doc_title: str = DEFAULT_UNTITLED_DOCUMENT_TITLE,
    organization: str | None = None,
    doc_id: str | None = None,
    embedder: Embedder | None = None,
    strategy: BaseChunker | None = None,
) -> ChunkNode:
    from adapters.lm_studio.embedder import LMStudioEmbedder

    embedder = embedder or LMStudioEmbedder()
    doc_id = doc_id or str(uuid.uuid4())
    doc_slug = slugify(doc_title)

    if strategy is None:
        paragraphs = split_paragraphs(text)
        strategy = (
            SemanticChunker(split_fn=segment_sentences)
            if len(paragraphs) <= 1
            else SemanticChunker(split_fn=split_paragraphs)
        )

    node_id = str(uuid.uuid4())
    flat_section = MarkdownSection(
        level=DOCUMENT_LEVEL,
        title=doc_title,
        content=text,
    )
    chunk_children = await _build_chunks(
        flat_section,
        embedder,
        doc_id,
        doc_slug,
        node_id,
        DOCUMENT_LEVEL + 1,
        strategy,
        document_style=DocumentStyle.FLAT,
    )

    return ChunkNode(
        id=node_id,
        doc_id=doc_id,
        node_type=NodeType.DOCUMENT,
        title=doc_title,
        level=DOCUMENT_LEVEL,
        section_path=doc_slug,
        organization=organization,
        children=chunk_children,
        document_style=DocumentStyle.FLAT,
    )
