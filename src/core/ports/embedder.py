from __future__ import annotations

from typing import Optional, Protocol


class Embedder(Protocol):
    async def embed(self, texts: list[str]) -> list[Optional[list[float]]]:
        ...
