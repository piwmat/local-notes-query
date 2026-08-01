# CONTEXT.md — Kontrakt Workspace

## Forma: Knowledge Bundle + Pipeline

Workspace łączy dwie formy ICM:
- **Knowledge Bundle** — `notes/` to nawigowalna wiedza (36 notatek, wikilinki).
- **Pipeline** — `notes/` → indeksy → query, powtarzalny przebieg z bramkami ludzkimi.

## Przepływ (jeden przebieg)

```
notes/*.md
   │  (1) update_tree.py      → output/tree-index.md      [drzewo wikilinków]
   │  (2) build_graph.py      → output/knowledge-graph.json [graf wiedzy]
   │  (3) enrich.py           → output/knowledge-graph.json [+ warstwy L0-L3, tour]
   │  (4) stamp.py / sync.bat → output/knowledge-graph.json [+ git hash]
   ▼
programs/local-kb.py  (REPL: pytanie → RAG → odpowiedź z cytatami)
```

## Kontrakty folderów

| Folder | Rola | Czyta | Pisze |
|---|---|---|---|
| `notes/` | Knowledge base (surowiec) | — | — (gitignored) |
| `programs/` | Factory: query + indeksy | `notes/` | `output/` |
| `tools/` | Factory: graf wiedzy | `output/knowledge-graph.json` | `output/knowledge-graph.json` |
| `output/` | Product: wygenerowane indeksy | — | — (przebudowywane) |
| `_archive/` | Dead: logi, nieaktualne | — | — |

## Factory vs Product

- **Factory (stabilne):** `programs/`, `tools/`, `AGENTS.md`, `IDENTITY.md`, `PROJECT_PRINCIPLES.md`
- **Product (nowe co przebieg):** `output/tree-index.md`, `output/knowledge-graph.json`

## Bramki ludzkie

1. Zmiana struktury folderów → akceptacja człowieka (ten plik + AGENTS.md).
2. `_archive/` → tylko za zgodą.
3. Migracja pliku między rolami → propozycja przed ruchem.

## Status

Status pipeline'u = skan `output/` (co istnieje, jaka data). Brak ręcznych edycji indeksów.
