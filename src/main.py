"""
Unified CLI entry point.

Usage:
    uv run python -m main ingest sample-contract.md
    uv run python -m main query "What are the payment terms?"
    uv run python -m main query --show-provenance
"""
from __future__ import annotations

import asyncio
import sys


async def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python -m main <command> [args...]")
        print("Commands:")
        print("  ingest   Ingest a document into Solr")
        print("  query    Query the RAG pipeline")
        return 1

    command = sys.argv[1]
    rest = sys.argv[2:]

    if command == "ingest":
        sys.argv = [sys.argv[0], *rest]
        from ingest.cli import main as ingest_main
        return await ingest_main()
    elif command == "query":
        sys.argv = [sys.argv[0], *rest]
        from rag.cli import main as query_main
        return await query_main()
    else:
        print(f"Unknown command: {command}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
