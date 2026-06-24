from __future__ import annotations

import argparse
import asyncio
import sys

from adapters.lm_studio.embedder import LMStudioEmbedder
from adapters.solr.client import SolrClient, DEFAULT_SOLR_BASE, DEFAULT_COLLECTION
from ingest.use_case import ingest_document


async def main() -> int:
    parser = argparse.ArgumentParser(
        description="Chunk a raw document and ingest into Solr."
    )
    parser.add_argument("input", type=str, help="Path to a .md or .txt file")
    parser.add_argument("--organization", type=str, default="org-default")
    parser.add_argument("--style", type=str, choices=["markdown", "flat", "auto"], default="auto")
    parser.add_argument("--solr-url", type=str, default=DEFAULT_SOLR_BASE)
    parser.add_argument("--collection", type=str, default=DEFAULT_COLLECTION)
    parser.add_argument("--delete-first", action="store_true")
    args = parser.parse_args()

    embedder = LMStudioEmbedder()
    solr = SolrClient(base_url=args.solr_url, collection=args.collection)

    try:
        summary = await ingest_document(
            input_path=args.input,
            embedder=embedder,
            store=solr,
            organization=args.organization,
            style=args.style,
            delete_first=args.delete_first,
        )
        print("Done.")
        print(f"Indexed: {summary}")
    finally:
        solr.close()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
