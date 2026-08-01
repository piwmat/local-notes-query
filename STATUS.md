# STATUS.md — Stan Workspace

*Ostatnia aktualizacja: 2026-08-01*

## Co jest zrobione

- [x] Notatki przeniesione do `notes/` (36 plików, gitignored)
- [x] Program przemianowany na `local-kb` (REPL, `/model` command)
- [x] ICM Restructure: `.ua/` → `tools/`, produkty → `output/`, logi → `_archive/`
- [x] Kontrakty: `AGENTS.md` (routing), `CONTEXT.md` (workspace), `CONTEXT.md` per stage
- [x] Kontrakty: `IDENTITY.md` (postawa audytora), `logbook.md`, niniejszy plik
- [x] Pipeline działa end-to-end (update_tree → build_graph → enrich → test_kb)
- [x] Git: 6 commitów (init, sync ×2, restructure, fix, fix)

## Aktualny stan pipeline'u

- `output/tree-index.md` — świeży (wygenerowany 2026-08-01)
- `output/knowledge-graph.json` — świeży (nodes=16, edges=11, layers=4, tour=10)
- `output/` i `_archive/` — gitignored (produkty nie są w git)

## Co jest następne (kolejka)

1. **Push do GitHub** (repo `piwmat/local-notes-query`) — zrobione.
2. **Ewaluacja retrievalu** — naprawiona (retrieve cmd w local-kb.py). Baseline: Recall@10=0.406, MRR=0.500. Następny cel: >0.6.
3. **`sync.bat` pełny przebieg** — przetestowany po naprawie `for /f`. Indeksowanie działa.

## Decyzje

- **Graf konceptów (rzeczowniki + krawędzie-czasowniki, styl Cognee): ODROCZONY.** Trigger: korpus >200 notatek LUB Recall@10 <0.6 po naprawach. Powód: koszt ekstrakcji LLM rośnie liniowo z liczbą notatek; embeddingi pokrywają semantykę przy małym korpusie. Upgrade path: LLM-extract triples offline → JSON → krawędzie do NEIGHBORS.

## Otwarte pytania

- Czy `queries.json` ma zostać w repo? (używany przez eval_retrieval.py → tak)

