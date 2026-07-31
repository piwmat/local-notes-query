# Agent Standard: Querying Knowledge Base

## Architecture
`./programs/query` — standalone Python script. Local ONNX embeddings, keyword MCP, MMR-based selection, LLM synthesis.

## Pipeline
1. **Deterministic retrieval** (0 tokens): question → local ONNX (bge-micro-v2) cosine vs `embeddings.json` (top 10) + keyword MCP search (top 8) → merged candidate list
2. **Deterministic MMR selection** (0 tokens): greedy Maximal Marginal Relevance over candidate embedding vectors — `λ·score − (1−λ)·max_sim(picked)`, λ=0.75, plus near-duplicate gate `DUP_THRESH=0.92` and **6k token hard cap** (no LLM; `tree-index.md` used only for ancestor-chain headers)
3. **Read notes** (0 tokens): script reads selected files from filesystem
4. **LLM synthesis** (tokens): question + layer-2 SCOPE header (budget used/left, branches) + selected note content (ancestor chains inline) + candidate list → answer with citations

## Files
- `./programs/query` — main query script
- `./programs/build-embeddings` — refresh embeddings from Smart Connections `.ajson` files
- `./programs/tree-index.md` — auto-generated knowledge tree (data, lives with programs)
- `embeddings.json` — pre-computed 384-dim vectors for all `best you/` notes (data, stays in vault root)

## Principles
- **Embeddings NEVER enter LLM context** — only paths and content.
- **Deterministic top-K** — reproducible, no randomness; MMR selection is bounded by the candidate list.
- **MMR decides what to read** — diversity via embedding similarity (λ=0.75, dupe gate 0.92), capped by 6k token budget; script does the file I/O.
- **Reference-based** — cite note filename per point.
- **Terse, engineering-focused, bulleted. No fluff.
