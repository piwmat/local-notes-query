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
- Sanity 2026-08-01: tree→graph→enrich→test_kb OK; eval **Recall@10=0.500, MRR=0.517** (baseline potwierdzony)

## Co jest następne (kolejka)

1. **Push do GitHub** (repo `piwmat/local-notes-query`) — zrobione, zweryfikowane 2026-08-01: origin/master = `1cd4cee`, brak rozjazdu.
2. **Ewaluacja retrievalu** — działa. Baseline: Recall@10=0.438, MRR=0.521 → po grafie konceptów: **Recall@10=0.500, MRR=0.517**. Następny cel: >0.6 (tuning decay krawędzi konceptowych).
3. **`sync.bat` pełny przebieg** — przetestowany po naprawie `for /f`. Indeksowanie działa.

## Decyzje

- **Środowisko uruchomieniowe:** skrypty z numpy (`local-kb.py`, `test_kb.py`, `eval_retrieval.py`) → `C:\Users\Mateusz\AppData\Local\anaconda3\python.exe` (numpy 2.3.5, onnxruntime, tokenizers). Domyślny `python` (hermes-agent venv) ich nie ma. `sync.bat`/narzędzia grafu = stdlib, działają na każdym pythonie.
- **Graf konceptów (Cognee-lite): ZBUDOWANY.** `tools/build_concept_graph.py` → `output/concept-graph.json` (416 triples) → `CONCEPT_NEIGHBORS` w local-kb.py. Recall@10 0.438→0.500. Do tuningu: decay krawędzi konceptowych (dilucja Q1/Q2/Q5).
- **Cognee (biblioteka): ODRZUCONE po A/B** (6 blokerów integracji z 9Router, m.in. JSON schema `discriminator` → 400). Szczegóły w logbook.md.

## Pętla weryfikacji (Dead Man's Switch)

Stan licznika nieudanych prób dla aktywnej pętli tuningowej (patrz `tools/verification-skill.md`,
`programs/loop_tune.py`). Limit: **3 kolejne nieudane próby** → twardy stop, raport do logbook.md.

- pętla_licznik: 0/3
- pętla_cel: brak aktywnej pętli
- pętla_ostatni_wynik: —

## Otwarte pytania

- Czy `queries.json` ma zostać w repo? (używany przez eval_retrieval.py → tak)

