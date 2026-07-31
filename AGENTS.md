# Agent Standard: Querying Knowledge Base

## Architecture
`./programs/best-you-kb.py` — single-file Python RAG. 0 external deps beyond numpy/onnxruntime/tokenizers. **Independent of Smart Connections.**

## Pipeline
1. **Boot** (~1-2s one-off): load `*.md` from `best you/`, embed title+branch via local ONNX (bge-micro-v2, 384-dim). No `embeddings.json` cache — vectors live in process memory.
2. **Vector retrieval** (0 LLM tokens): ONNX embed question → cosine top-10 vs in-memory note vecs.
3. **Keyword retrieval** (0 LLM tokens): in-process TF-IDF (BM25-ish, ~30 lines of numpy) → top-8. Replaces Smart Connections MCP.
4. **Hybrid candidates**: union of (vector, keyword) with vector score × 1.0, keyword × 0.7.
5. **MMR selection** (0 LLM tokens): `λ·score − (1−λ)·max_sim(picked)`, λ=0.75, dupe gate `DUP_THRESH=0.92`, **6k token hard cap**.
6. **LLM synthesis** (tokens): question + selected note content + ancestor chain → answer with citations.

## Files
- `./programs/best-you-kb.py` — single-file REPL (query, retrieve, synthesize).
- `./programs/update_tree.py` — regenerate `tree-index.md` from wikilinks.
- `./programs/tree-index.md` — auto-generated knowledge tree.
- `./.ua/knowledge-graph.json` — UA dashboard graph.
- `./AGENTS.md` — this file.
- `./embeddings.json` — **deprecated** (kept for back-compat; best-you-kb.py does not use it).

## Config (env)
- `LLM_BASE` (default `http://localhost:20128/v1`)
- `LLM_API_KEY` (optional)
- `LLM_MODEL` (default `oc/ling-3.0-flash-free`)

## Principles
- **Embeddingi generowane in-process** — notatki raz przy bocie, pytania per-query. SC nie jest wymagany.
- **Deterministic top-K** — zero randomness; MMR bounded by candidate list.
- **Hybrid retrieval** — vector + TF-IDF, hybrid recall > either alone.
- **Reference-based** — cite filename per point.
- **Terse, engineering-focused, bulleted. No fluff.**