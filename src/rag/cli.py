from __future__ import annotations

import argparse
import asyncio
import sys

from adapters.lm_studio.embedder import LMStudioEmbedder
from adapters.lm_studio.llm import LMStudioLLM
from adapters.solr.client import SolrClient, DEFAULT_SOLR_BASE, DEFAULT_COLLECTION
from adapters.solr.store import SolrDocumentStore
from core.constants.reranker import ALPHA, BETA, TOP_K
from rag.router import RagRouter


async def main() -> int:
    parser = argparse.ArgumentParser(
        description="Query the hybrid RAG pipeline."
    )
    parser.add_argument(
        "query", type=str, nargs="?",
        help="Question to answer. If omitted, enters interactive mode."
    )
    parser.add_argument("--solr-url", type=str, default=DEFAULT_SOLR_BASE)
    parser.add_argument("--collection", type=str, default=DEFAULT_COLLECTION)
    parser.add_argument("--top-k", type=int, default=TOP_K)
    parser.add_argument("--alpha", type=float, default=ALPHA)
    parser.add_argument("--beta", type=float, default=BETA)
    parser.add_argument("--show-context", action="store_true")
    parser.add_argument("--show-provenance", action="store_true")
    args = parser.parse_args()

    embedder = LMStudioEmbedder()
    llm = LMStudioLLM()
    solr = SolrClient(base_url=args.solr_url, collection=args.collection)
    store = SolrDocumentStore(solr)
    router = RagRouter(
        embedder=embedder, llm=llm, store=store,
        top_k=args.top_k, alpha=args.alpha, beta=args.beta,
    )

    if args.query:
        queries = [args.query]
    else:
        print("Interactive RAG query mode. Type your question or '/quit' to exit.")
        queries = []
        while True:
            try:
                q = input(">>> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not q:
                continue
            if q.lower() in ("/quit", "/exit", "/q"):
                break
            queries.append(q)

    for q in queries:
        print()
        print(f"Query: {q}")
        print("-" * 60)

        if args.show_provenance or args.show_context:
            embedding_result = await embedder.embed([q])
            if not embedding_result or not embedding_result[0]:
                print("Error: Failed to embed query.")
                continue
            query_vector = embedding_result[0]

            ranked = await router.retrieve(q, query_vector)
            print(f"Ranked top {len(ranked)} chunks.")

            if args.show_provenance:
                print("\nProvenance:")
                for i, c in enumerate(ranked):
                    p = c.provenance
                    print(
                        f"  {i + 1}. [{p['retrieval_source']}]\n"
                        f"     bm25_score={p['bm25_score']}, vector_score={p['vector_score']}\n"
                        f"     bm25_norm={p['bm25_norm']}, vector_norm={p['vector_norm']}\n"
                        f"     S1 = {p['s1_formula']} = {p['s1']}\n"
                        f"     dist={p['distance']}, S2 = {p['s2_formula']} = {p['s2']}\n"
                        f"     final = {p['final_formula']} = {p['final_score']}\n"
                        f"     id={p['id']}\n"
                        f"     content=\"{p['content']}\""
                    )

            context = None
            if args.show_context:
                from rag.generation.context import ContextBuilder
                cb = ContextBuilder()
                context = cb.build(ranked)
                print("\nContext:")
                print(context)
                print()

        answer = await router.answer(q)
        print(f"\nAnswer:\n{answer}")

    solr.close()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
