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
2. **Ewaluacja retrievalu** — naprawiona (retrieve cmd + fix benchmarku cudzysłowów). Baseline: Recall@10=0.438, MRR=0.521. Następny cel: >0.6 (graf konceptów).
3. **`sync.bat` pełny przebieg** — przetestowany po naprawie `for /f`. Indeksowanie działa.

## Decyzje

- **Graf konceptów (rzeczowniki + krawędzie-czasowniki): BUDUJEMY (Cognee-lite), trigger spełniony.** Recall@10=0.438 <0.6. Sposób: własna ekstrakcja triples (1× LLM batch, plain chat completion) → `output/concept-graph.json` → krawędzie do NEIGHBORS. Bez instructor/graph DB.
- **Cognee (biblioteka): ODRZUCONE po A/B** (6 blokerów integracji z 9Router, m.in. JSON schema `discriminator` → 400). Szczegóły w logbook.md.

## Otwarte pytania

- Czy `queries.json` ma zostać w repo? (używany przez eval_retrieval.py → tak)

