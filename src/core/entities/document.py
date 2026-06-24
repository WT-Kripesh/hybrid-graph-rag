from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MarkdownSection:
    level: int
    title: str
    content: str
    children: list[MarkdownSection] = field(default_factory=list)
