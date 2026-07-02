from __future__ import annotations

from abc import ABC, abstractmethod

from core.entities.text_chunk import TextChunk


class BaseChunker(ABC):
    @abstractmethod
    async def chunk(
        self, text: str, embedder: "Embedder"  # noqa: F821
    ) -> list[TextChunk]:
        pass
