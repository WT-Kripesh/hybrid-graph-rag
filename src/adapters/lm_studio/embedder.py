from __future__ import annotations

from typing import Optional

import httpx

from core.constants.api import (
    API_FIELD_DATA,
    API_FIELD_EMBEDDING,
    API_FIELD_INDEX,
    API_FIELD_INPUT,
    API_FIELD_MODEL,
    DEFAULT_API_INDEX,
    DEFAULT_EMBEDDING_DIM,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_EMBEDDINGS_URL,
    DEFAULT_TIMEOUT_SECONDS,
)


class LMStudioEmbedder:
    def __init__(
        self,
        base_url: str = DEFAULT_EMBEDDINGS_URL,
        model: str = DEFAULT_EMBEDDING_MODEL,
        dim: int = DEFAULT_EMBEDDING_DIM,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.base_url = base_url
        self.model = model
        self.dim = dim
        self.timeout = timeout

    async def embed(self, texts: list[str]) -> list[Optional[list[float]]]:
        if not texts:
            return []
        try:
            return await self._embed_remote(texts)
        except Exception:
            return [None] * len(texts)

    async def _embed_remote(self, texts: list[str]) -> list[list[float]]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                json={API_FIELD_MODEL: self.model, API_FIELD_INPUT: texts},
                timeout=self.timeout,
            )
        response.raise_for_status()
        payload = response.json()
        ordered = sorted(
            payload[API_FIELD_DATA],
            key=lambda item: item.get(API_FIELD_INDEX, DEFAULT_API_INDEX),
        )
        return [item[API_FIELD_EMBEDDING] for item in ordered]
