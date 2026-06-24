from __future__ import annotations

from typing import Optional, Protocol


class LLM(Protocol):
    async def generate(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> Optional[str]:
        ...
