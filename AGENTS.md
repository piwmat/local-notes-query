# AGENTS.md — Mapa Workspace

Jesteś w workspace `best you` — lokalna baza wiedzy o samodyscyplinie z pipeline'em
indeksowania i odpytywania. Struktura folderów JEST architekturą (ICM, arXiv:2603.16021).

## Routing

| Zadanie | Idź do |
|---|---|
| Stan workspace / co dalej | `STATUS.md` |
| Historia działań i błędów | `logbook.md` |
| Tożsamość i postawa agenta | `IDENTITY.md` |
| Odpytywanie notatek (REPL) | `programs/local-kb.py` (uruchom przez `programs/local-kb.bat`) |
| Zbuduj tree-index | `programs/update_tree.py` → zapisuje `output/tree-index.md` |
| Zbuduj graf wiedzy | `tools/build_graph.py` → `output/knowledge-graph.json` |
| Wzbogać graf (warstwy/tour) | `tools/enrich.py` |
| Przepisz graf | `tools/rewrite_graph.py` |
| Pełny sync (tree+graf+commit) | `programs/sync.bat` |
| Ewaluacja retrievalu | `programs/eval_retrieval.py` (+ `programs/queries.json`) |
| Eksperyment: Cognee | `programs/cognee_pipeline.py` |

## Konwencje

- Notatki: `notes/*.md` — GITIGNORED, prywatne. Nie zmieniaj bez potrzeby.
- Ścieżki w skryptach: względne do roota workspace (patrz `update_tree.py`, `sync.bat`).
- Produkty (wygenerowane): `output/` — NIE edytuj ręcznie; przebuduj skryptem.
- Martwe pliki: `_archive/` — nigdy nie usuwaj bez akceptacji człowieka.
- Model LLM: `LLM_MODEL` env (domyślnie `oc/ling-3.0-flash-free`), zmiana w REPL przez `/model`.

## Zasady agenta

- Czytaj `PROJECT_PRINCIPLES.md` i `IDENTITY.md` przed zmianami.
- Każda zmiana struktury → najpierw propozycja + akceptacja (bramka ludzka).
- Weryfikuj zmiany (uruchom skrypt) przed zakończeniem.
- **Stop i raportuj:** jeśli coś zawiedzie — przerwij i raportuj. Cichy retry zakazany.
- Po każdym zadaniu: wpis do `logbook.md` + aktualizacja `STATUS.md`.
