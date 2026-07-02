from __future__ import annotations

from typing import Iterator

from core.constants.chunker import BLANK_CHAR, DEFAULT_FIXED_CHUNK_OVERLAP, DEFAULT_FIXED_CHUNK_SIZE
from core.entities.text_chunk import TextChunk
from core.ports.chunker import BaseChunker
from core.ports.embedder import Embedder


def _word_slices(
    words: list[str], chunk_size: int, step: int
) -> Iterator[list[str]]:
    n = len(words)
    for start in range(0, n, step):
        yield words[start : start + chunk_size]
        if start + chunk_size >= n:
            break


class FixedSizeChunker(BaseChunker):
    def __init__(
        self,
        chunk_size: int = DEFAULT_FIXED_CHUNK_SIZE,
        overlap: int = DEFAULT_FIXED_CHUNK_OVERLAP,
    ) -> None:
        if overlap < 0:
            raise ValueError(f"overlap must be non-negative, got {overlap}")
        if overlap >= chunk_size:
            raise ValueError(
                f"overlap ({overlap}) must be strictly less than "
                f"chunk_size ({chunk_size})"
            )
        self._chunk_size = chunk_size
        self._overlap = overlap
        self._step = chunk_size - overlap

    async def chunk(
        self, text: str, embedder: Embedder | None = None
    ) -> list[TextChunk]:
        words = text.split()
        if not words:
            return []
        return [
            TextChunk(text=BLANK_CHAR.join(window))
            for window in _word_slices(words, self._chunk_size, self._step)
        ]

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"chunk_size={self._chunk_size}, "
            f"overlap={self._overlap})"
        )
