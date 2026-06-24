from __future__ import annotations

from core.constants.reranker import ALPHA, BETA, TOP_K
from core.ports.embedder import Embedder
from core.ports.llm import LLM
from core.ports.store import DocumentStore
from rag.generation.context import ContextBuilder
from rag.generation.prompt import RAG_PROMPT
from rag.retrieval.hierarchy import HierarchyExpander
from rag.retrieval.hybrid import HybridRetriever
from rag.reranker.reranker import Reranker


class RagRouter:
    def __init__(
        self,
        embedder: Embedder,
        llm: LLM,
        store: DocumentStore,
        top_k: int = TOP_K,
        alpha: float = ALPHA,
        beta: float = BETA,
    ) -> None:
        self._embedder = embedder
        self._llm = llm
        self._retriever = HybridRetriever(store)
        self._expander = HierarchyExpander(store)
        self._reranker = Reranker(top_k=top_k, alpha=alpha, beta=beta)
        self._context_builder = ContextBuilder()

    async def answer(self, query: str) -> str | None:
        embedding_result = await self._embedder.embed([query])
        if not embedding_result or not embedding_result[0]:
            raise RuntimeError(
                "Failed to embed query. Ensure the embedding server is running."
            )
        query_vector = embedding_result[0]

        retrieved = self._retriever.retrieve(query, query_vector)
        expanded = self._expander.expand(retrieved)
        ranked = self._reranker.rerank(expanded)
        context = self._context_builder.build(ranked)

        prompt = RAG_PROMPT.format(query=query, context=context)
        return await self._llm.generate(prompt)

    async def retrieve(
        self, query: str, query_vector: list[float]
    ) -> list[object]:
        retrieved = self._retriever.retrieve(query, query_vector)
        expanded = self._expander.expand(retrieved)
        ranked = self._reranker.rerank(expanded)
        return ranked
