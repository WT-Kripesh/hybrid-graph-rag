from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TextChunk:
    text: str
    coherence_score: float | None = field(default=None)
