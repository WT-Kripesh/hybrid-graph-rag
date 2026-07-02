from __future__ import annotations

from core.constants.generation import NODE_HEADER, SECTION_SEPARATOR
from core.entities.scored_chunk import ScoredChunk


def _format_node(c: ScoredChunk) -> str:
    lines: list[str] = [
        NODE_HEADER.format(node_type=c.node_type.upper()),
        c.title,
    ]
    if c.content:
        lines.append("")
        lines.append(c.content)
    return "\n".join(lines)


class ContextBuilder:
    def build(self, chunks: list[ScoredChunk]) -> str:
        parts = [_format_node(c) for c in chunks]
        return SECTION_SEPARATOR.join(parts)
