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

1. **Push do GitHub** (repo `piwmat/local-kb`?) — czeka na utworzenie repo przez użytkownika
2. **Decyzja: specjaliści** (`_system/security`, `_system/quality`) — wstrzymane (YAGNI, projekt mały)
3. **Ewaluacja retrievalu** — `programs/eval_retrieval.py` + `queries.json` (benchmark jakości)
4. **`sync.bat` pełny przebieg** — przetestowany po naprawie `for /f`

## Otwarte pytania

- Czy `queries.json` ma zostać w repo? (używany przez eval_retrieval.py → tak)
- Czy cognee_pipeline.py ma pozostać? (eksperymentalny, nieaktywny)
