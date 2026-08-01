# CONTEXT.md — Stage: tools/ (Factory: graf wiedzy)

## Zadanie
Budowa i utrzymanie grafu wiedzy (knowledge graph) workspace.

## Czyta (input)
- `notes/*.md` — źródło (tytuły, wikilinki)
- `output/knowledge-graph.json` — graf do wzbogacenia (enrich/rewrite)

## Proces
- `build_graph.py` — buduje graf z vaultu (nodes: file/resource/service, edges).
- `enrich.py` — dodaje warstwy L0-L3 i tour (10 kroków) do grafu.
- `rewrite_graph.py` — przebudowuje strukturę grafu (usuwa martwe odwołania).
- `stamp.py` — wpina git hash + timestamp do grafu.
- `test_kb.py` — sanity-check struktury grafu.

## Pisze (output)
- `output/knowledge-graph.json`

## Kontrola ludzka
- Graf ładuje się w dashboardzie (nodes/edges/liczby sensowne).
- `test_kb.py` przechodzi.
