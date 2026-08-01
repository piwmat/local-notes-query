
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

## 2026-08-01 — Ewaluacja naprawiona + decyzja o grafie konceptów

**Co zrobiono:**
- Dodano komendę `retrieve` do `local-kb.py` (CLI: `retrieve <q> --topk <k>`), której oczekiwał `eval_retrieval.py` — naprawia harness ewaluacyjny.
- A/B test embeddingów: pełny tekst notatki vs title+branch. **Wynik: pełny tekst gorszy** (Recall 0.344 vs 0.406, MRR 0.528 vs 0.500). Truncacja 512 tokenów rozwadnia sygnał opisowych tytułów. Zostawiono title+branch.
- Baseline ewaluacji (realny pipeline, bez bypass MMR): **Recall@10=0.406, MRR=0.500**.
- Decyzja zapisana w STATUS.md: graf konceptów (rzeczowniki+krawędzie, styl Cognee) ODROCZONY. Trigger: >200 notatek LUB Recall <0.6.

**Błędy napotkane:**
- Początkowe porównanie wyników mylące — poprzedni pomiar 0.406 był z `lam=1.0, budget=99999` (bypass MMR), nowy z realnym pipeline'em. Dopiero A/B (oba z realnym MMR) dał uczciwe porównanie.

**Status:** ✅ Zakończone. Harness działa, baseline ustalony.
