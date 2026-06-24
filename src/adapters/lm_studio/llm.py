from __future__ import annotations

from typing import Optional

import httpx

from core.constants.api import (
    API_FIELD_CHOICES,
    API_FIELD_MESSAGE,
    API_FIELD_MESSAGES,
    API_FIELD_MODEL,
    API_FIELD_ROLE,
    DEFAULT_CHAT_MODEL,
    DEFAULT_CHAT_URL,
    DEFAULT_TIMEOUT_SECONDS,
    FIELD_CONTENT,
    ROLE_SYSTEM,
    ROLE_USER,
)


class LMStudioLLM:
    def __init__(
        self,
        base_url: str = DEFAULT_CHAT_URL,
        model: str = DEFAULT_CHAT_MODEL,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.base_url = base_url
        self.model = model
        self.timeout = timeout

    async def generate(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> Optional[str]:
        messages = []
        if system_prompt:
            messages.append(
                {API_FIELD_ROLE: ROLE_SYSTEM, FIELD_CONTENT: system_prompt}
            )
        messages.append({API_FIELD_ROLE: ROLE_USER, FIELD_CONTENT: prompt})

        try:
            return await self._generate_remote(messages)
        except Exception:
            return None

    async def _generate_remote(self, messages: list[dict[str, str]]) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                json={
                    API_FIELD_MODEL: self.model,
                    API_FIELD_MESSAGES: messages,
                },
                timeout=self.timeout,
            )
        response.raise_for_status()
        payload = response.json()
        return payload[API_FIELD_CHOICES][0][API_FIELD_MESSAGE][FIELD_CONTENT]
