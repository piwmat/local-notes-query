# CONTEXT.md — Stage: programs/ (Factory: query + indeksy)

## Zadanie
Kod wykonywalny użytkownika: odpytywanie bazy wiedzy i budowa indeksów.

## Czyta (input)
- `notes/*.md` — surowe notatki (via `local-kb.py`, `update_tree.py`)
- `programs/queries.json` — benchmark pytań (via `eval_retrieval.py`)

## Proces
- `local-kb.py` — REPL RAG: embed (ONNX bge-micro-v2) + TF-IDF + wikilink graph + MMR → LLM.
- `update_tree.py` — wikilinki → `output/tree-index.md`.
- `eval_retrieval.py` — ewaluacja trafności retrievalu.
- `cognee_pipeline.py` — eksperymentalny backend Cognee (nieaktywny).
- `sync.bat` — pełny przebieg: tree → graf → enrich → stamp → git commit.

## Pisze (output)
- `output/tree-index.md`
- (pośrednio przez sync) `output/knowledge-graph.json`

## Kontrola ludzka
- Odpowiedź LLM jest poprawna i cytuje źródła.
- `sync.bat` kończy się bez błędów i robi commit.
- `local-kb.bat` uruchamia REPL na właściwym interpreterze (anaconda3).
