
---

## 2026-08-01 — Naprawa i Ewaluacja Pipeline'u

**Co zrobiono:**
- Zdiagnozowano i naprawiono błąd w `update_tree.py`, który niepoprawnie obsługiwał ścieżki do notatek po restrukturyzacji (przeniesieniu do `notes/`). Skrypt czytał z roota zamiast `notes/` → pusty tree-index.
- Uruchomiono `eval_retrieval.py` i zdiagnozowano, dlaczego zwracał zerowe wyniki. Problem leżał w serii błędów:
    1. Brak `numpy` w środowisku `uv`.
    2. Nieaktualna ścieżka do Pythona w Anacondzie.
    3. Nieaktualny `tree-index.md`.
    4. Niedopasowanie logiki i formatu wyjścia między `eval_retrieval.py` a `local-kb.py` (brak komendy `retrieve`).
- Po tymczasowych poprawkach (bypass MMR: lam=1.0, budget=99999) `eval_retrieval.py` zwrócił `Recall@10 = 0.406`, `MRR = 0.500`.
- Tymczasowe zmiany w `local-kb.py` i `eval_retrieval.py` zostały wycofane. Trwała poprawka została tylko w `update_tree.py`.
- Sprawdzono pliki cognee — nie istnieją (usunięte wcześniej; AGENTS.md/STATUS.md zawierały nieaktualne wzmianki).
- Zaktualizowano `STATUS.md`.

**Błędy napotkane:**
- `ModuleNotFoundError: numpy` przy uruchamianiu skryptów ewaluacyjnych.
- `eval_retrieval.py` zwracał `Recall=0` — wiele czynników, głównie brak komendy `retrieve` i nieaktualny indeks.
- Próba przywrócenia plików przez `mv` z `git show` zawiodła (ścieżki Windows/bash), wymagając `write_file`.

**Status:** ✅ Zakończone. Główny pipeline działa. Ewaluacja wymagała osobnej naprawy (patrz niżej).

---

## 2026-08-01 — Tuning CONCEPT_DECAY: optimum 0.5, eksperyment zamknięty

**Co zrobiono:** A/B/C decay krawędzi konceptowych w `candidates()`.
- 0.3 → Recall 0.469 (dilucja odwrócona — za słaba ekspansja)
- **0.5 → 0.500 (optymalne, zgodne z GRAPH_DECAY)** ← zostaje
- 0.7 → Recall 0.406, MRR 0.495 (za silna ekspansja wypycha seeds)

**Wniosek:** GRAPH_DECAY=0.5 dla obu typów krawędzi jest punktem równowagi. Brak dalszych knobów wartych kręcenia; następny skok Recall wymagałby innego sygnału (np. lepsze embeddingi).

**Status:** ✅ Zakończone. `CONCEPT_DECAY=0.5` udokumentowany w kodzie.

---

## 2026-08-01 — Cognee-lite: graf konceptów zbudowany i zintegrowany — Recall 0.438→0.500

**Co zrobiono:**
- `tools/build_concept_graph.py` (nowy): per-note LLM batch (plain chat completion, `stream:false`), ekstrakcja triples (podmiot, czasownik, dopełnienie) → `output/concept-graph.json`. 36 notatek, 416 triples, 1 empty (excalibrain 1.md — Excalidraw bez tekstu), 66s.
- `local-kb.py`: ładowanie grafu → `CONCEPT_NEIGHBORS` (notatki dzielące ≥1 koncept s/o) → ekspansja w `candidates()` z `GRAPH_DECAY`.
- Eval (bramka danych): **Recall@10 0.438→0.500, MRR 0.521→0.517**. PASS → graf zostaje.

**Wzorce:**
- Trafione cele fleksji: Q6 (zagraża→Zagrożenia) 0→1, Q10 (doraźna→Doraźne) 0→2, Q4 0→2.
- Dilucja: Q1/Q2/Q5 straciły po 1-2 hitach (koncept-edge'y wypychają bezpośrednie). Kandydat do tuningu: niższy decay dla krawędzi konceptowych.

**Błędy napotkane:**
- 9Router domyślnie zwraca SSE stream (`text/event-stream`) gdy brak `"stream": false` w body → `json.loads` fail. Fix: `"stream": False`. (lekcja: curl z jawnym `stream:false` maskował problem)

**Status:** ✅ Zakończone. Graf działa, recall poprawiony.

---

## 2026-08-01 — A/B test: cognee vs własny pipeline — WYNIK: cognee odrzucone

**Co zrobiono:**
- Test integracji cognee 1.4.0 (zainstalowane w anaconda) z endpointem 9Router (localhost:20128).
- Ścieżka LLM działa (litellm → `openai/gc/gemini-2.5-flash-lite` → `OK: 4`).

**Błędy napotkane (6 blokerów):**
1. `set_llm_provider("litellm")` — nie ma w enum LLMProvider 1.4.0 (openai/ollama/anthropic/custom/gemini/mistral/azure/bedrock/llama_cpp) → `openai`
2. `test_llm_connection` timeout 30s → `COGNEE_SKIP_CONNECTION_TEST=true`
3. Nazwa datasetu ze ścieżki: "best you" (spacja) → ValueError → kopia notatek do `%TEMP%\best-you-notes`
4. Model `ollama/minimax-m3` → litellm routuje po prefiksie na protokół ollama → 404 HTML 9Router
5. Brak credentials per provider → model z `gc/` działa
6. **Ściana:** instructor (pydantic→JSON schema z `discriminator`) → gemini-cli: `400 INVALID_ARGUMENT Unknown name "discriminator"` → InstructorRetryException pętla retry. Wymaga custom adaptera — koniec testu.

**Wniosek:** cognee nie integruje się z 9Router bez chirurgii. Koszt > wartość. **Cognee-lite (własna ekstrakcja triples, plain chat completion, bez instructor/graph DB) pozostaje rekomendacją.**

**Status:** ✅ Zakończone (negatywny wynik = wynik). `.cognee_*` storage w `~` — partial data, nieużywane.

---

## 2026-08-01 — Ewaluacja naprawiona + decyzja o grafie konceptów

**Co zrobiono:**
- Dodano komendę `retrieve` do `local-kb.py` (CLI: `retrieve <q> --topk <k>`), której oczekiwał `eval_retrieval.py` — naprawia harness ewaluacyjny.
- A/B test embeddingów: pełny tekst notatki vs title+branch. **Wynik: pełny tekst gorszy** (Recall 0.344 vs 0.406, MRR 0.528 vs 0.500). Truncacja 512 tokenów rozwadnia sygnał opisowych tytułów. Zostawiono title+branch.
- Baseline ewaluacji (realny pipeline, bez bypass MMR): **Recall@10=0.406, MRR=0.500**.
- Decyzja zapisana w STATUS.md: graf konceptów (rzeczowniki+krawędzie, styl Cognee) ODROCZONY. Trigger: >200 notatek LUB Recall <0.6.

**Błędy napotkane:**
- Początkowe porównanie wyników mylące — poprzedni pomiar 0.406 był z `lam=1.0, budget=99999` (bypass MMR), nowy z realnym pipeline'em. Dopiero A/B (oba z realnym MMR) dał uczciwe porównanie.

**Status:** ✅ Zakończone. Harness działa, baseline ustalony.
