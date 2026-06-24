# Hybrid Graph RAG Chunker — Retrieval System

## What this system does

This is a **retrieval-augmented generation (RAG)** system that answers questions about your documents. Instead of returning a list of search results, it reads the most relevant passages from your documents and produces a natural-language answer. It is designed for **markdown documents** like contracts, policies, reports, or any structured text.

The system supports **two key workflows**:

- **Ingestion** — feed it a `.md` file, and it is chunked into intelligible pieces, converted to embeddings (vector representations), and indexed for both keyword and semantic search.
- **Query** — ask a question in plain English; the system retrieves the most relevant chunks, optionally expands them with their parent sections for context, reranks them by relevance, and sends the best context to an LLM to produce an answer.

Out of the box it runs on **Solr** (for indexing and search) and **LM Studio** (for embeddings and chat), both containerized or running locally.

---

## How this is different from a standard RAG

Most RAG systems either give you a **dumb keyword search** or a **pure vector search** with a flat list of chunks. This system layers multiple signals:

| Typical RAG | This system |
|---|---|
| One retrieval method (BM25 *or* vector) | **Hybrid** — BM25 + vector scores blended together |
| Flat chunks, no structure awareness | **Hierarchical** — knows document → section → chunk and preserves parent context |
| Top-k cutoff with raw scores | **Two-stage scoring** — relevance (S1) + proximity (S2) combined via configurable weights |
| Scores are opaque | **Transparent provenance** — exact formula and numeric values shown per chunk |
| Standard prompt | **Anti-hallucination** prompt that forces "I don't know" over fabrication |
| Picks only leaf chunks | **Ancestor expansion** — walks the parent chain to include structural context |

---

## Unique features in detail

### 1. Hybrid retrieval with min-max normalization

When a query arrives, the system fires **two parallel searches** against Solr:

- **BM25** — keyword-based (Solr's edismax query parser weighting `content^4 title^2`)
- **Vector / KNN** — semantic similarity using cosine distance on 768-dim embeddings

Each result set has its own raw scoring scale. To blend them, raw scores are **independently min-max normalized** across all candidates, producing `norm_bm25` and `norm_vector`. They are then combined:

```
S1 = 0.4 × norm_bm25 + 0.6 × norm_vector
```

- `alpha = 0.4` and `beta = 0.6` are **configurable**.
- A document found by both methods gets a rich hybrid score.
- A document found only by one method gets `0` weight from the other.

### 2. Hierarchy expansion

Documents are chunked into a tree: **document → section → chunk**. Each chunk stores its `parent_id` and `section_path`. After retrieval, the system walks the parent chain (up to `MAX_DEPTH = 2`) and injects ancestor chunks into the candidate pool.

This means if the best-matching chunk is a sentence buried deep in a section, the system also sees the section heading and the document title — giving the LLM **structural context**, not just isolated fragments.

### 3. Two-stage scoring: S1 + S2

Every chunk gets two scores:

- **S1 (relevance)** — how well the chunk matches the query, computed from the hybrid BM25 + vector normalization above.
- **S2 (proximity)** — a structural bonus for being close to the retrieved chunk in the document tree:

```
S2 = 1 / (1 + distance)
```
  - Original chunk: `dist=0` → `S2 = 1.0`
  - Immediate parent: `dist=1` → `S2 = 0.5`
  - Grandparent: `dist=2` → `S2 = 0.333`

The final ranking score blends both:

```
final = 0.8 × S1 + 0.2 × S2
```

This means **relevance matters most**, but nearby parent chunks get a small boost so the LLM sees broader context.

### 4. Transparent provenance

Every chunk returned carries a **full audit trail** showing exactly how every number was derived:

```
bm25_score=3.8714, vector_score=0.8175
bm25_norm=1.0, vector_norm=0.9498
S1 = 0.4*1.0000 + 0.6*0.9498 = 0.9699
dist=0, S2 = 1/(1+0) = 1.0
final = 0.8*0.9699 + 0.2*1.0000 = 0.9759
content="Payments shall be made via bank transfer..."
```

This makes the system debuggable, explainable, and tunable.

### 5. Anti-hallucination generation

The generation prompt contains explicit instructions to avoid fabrication:

- "If the context does not contain enough information, say 'I don't know'."
- "Do NOT make up or infer facts not present in the context."
- "If no context is provided, respond only with 'I don't have enough information to answer that.'"

This reduces hallucination risk compared to open-ended LLM prompting.

### 6. Fully configurable pipeline

All major knobs are exposed as CLI parameters or environment variables:

- `--top-k` — number of chunks to retrieve and rerank
- `--alpha` — BM25 weight in S1 (default 0.4)
- `--beta` — vector weight in S1 (default 0.6)
- `ALPHA` / `BETA` in `scorer.py` — S1 vs S2 weights in final score
- `MAX_DEPTH` in `hierarchy_expander.py` — ancestor depth limit
- Model selection via environment variables for embedding and chat

No code changes needed to tune behaviour.

### 7. Production-grade index (Solr)

Instead of an in-memory vector store, the system uses **Apache Solr 10** with:

- A managed schema with `knn_vector` field type (768-dim, cosine similarity)
- Edismax query parser for tuned BM25
- Real index persistence, commits, and rollback
- Standard Solr API for monitoring (admin UI, metrics, logging)
- Docker-based deployment with a single `make solr-up`

### 8. Semantic chunker with tail-call optimization

The markdown chunker:

- Parses headings into a tree structure (document → sections → chunks)
- Uses semantic similarity (embedding cosine distance) to split oversize sections
- Employs **tail-call optimization** (TCO) to handle deeply nested documents without stack overflow
- Can fall back to fixed-size splitting when needed
- Produces Solr-compatible JSON with all structural fields preserved

---

## Architecture overview

```
┌────────────┐     ┌──────────────┐     ┌──────────────┐
│  Markdown  │────▶│   Chunker    │────▶│   Ingestion  │────▶ Solr
│  Document  │     │ (tree + TCO) │     │ (embed +     │     (BM25 +
└────────────┘     └──────────────┘     │  index)      │     KNN)
                                         └──────────────┘

┌────────────┐     ┌──────────────┐     ┌──────────────┐     ┌────────────┐
│  Query     │────▶│  Hybrid      │────▶│  Hierarchy   │────▶│  Reranker  │
│  (text)    │     │  Retriever   │     │  Expander    │     │  (S1 + S2) │
└────────────┘     │  BM25+vector │     └──────────────┘     └──────┬─────┘
                   └──────────────┘                                 │
                                                                    ▼
              ┌────────────┐     ┌──────────────┐     ┌──────────────┐
              │  Answer    │◀────│  LLM +       │◀────│  Context     │
              │  (text)    │     │  RAG prompt  │     │  Builder     │
              └────────────┘     └──────────────┘     └──────────────┘
```

---

## Project structure

```
src/
├── hybrid_graph_rag_chunker/    # Core chunker library
│   ├── chunk_builder.py         # Tree-based markdown chunker with TCO
│   ├── semantic_chunker.py      # Semantic similarity splitting
│   ├── constants.py             # Default model, dimensions
│   └── ai_client.py             # Embedding + LLM clients
├── solr/
│   ├── client.py                # Solr HTTP client (BM25 + KNN queries)
│   └── schema.json              # Solr managed schema definition
├── ingestion/
│   └── ingest_document.py       # CLI: chunk + embed + index into Solr
├── retrieval/
│   ├── hybrid_retriever.py      # Parallel BM25 + vector retrieval + normalization
│   └── hierarchy_expander.py    # Parent-chain walker for structural context
├── reranker/
│   ├── scorer.py                # ScoredChunk dataclass, all score formulas
│   └── reranker.py              # Reranker: provenance + final sort
├── generation/
│   ├── pipeline.py              # RetrievalPipeline orchestrator
│   ├── query.py                 # CLI: interactive or single-query mode
│   └── context_builder.py       # Assembles context blocks for the LLM
├── tests/                       # Integration tests
└── README.md                    # This file
```

---

## Quick start

See the top-level `Makefile` for common commands:

```bash
# Start Solr container + create core + apply schema
make solr-up

# Ingest a markdown document
make ingest-doc file=sample-contract.md

# Query (interactive)
make query

# Query with full provenance
uv run python -m generation.query "What are the payment terms?" --show-provenance

# Offline tests (no infra needed)
make test
```

**Prerequisites:** Docker (for Solr), LM Studio running on `localhost:1234` with a 768-dim embedding model and a chat model loaded.
