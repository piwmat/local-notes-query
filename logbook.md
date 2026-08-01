# Logbook — Czarna Skrzynka

Zapis działań agenta: co zrobiono, jakie błędy napotkano, status. Przeglądaj całość, by znaleźć powtarzające się wzorce awarii.

---

## 2026-08-01 — Restrukturyzacja ICM workspace

**Co zrobiono:**
- Notatki przeniesione `best you/` → `notes/` (36 plików), `.gitignore` + `notes/`
- Program przemianowany `best-you-kb` → `local-kb` (py, bat, prompt REPL)
- Dodany `/model` command do REPL (zmiana LLM w sesji)
- ICM Restructure (commit `abbe874`): `.ua/` → `tools/`, produkty → `output/`, logi → `_archive/`
- Kontrakty: `AGENTS.md`, `CONTEXT.md`, `IDENTITY.md`, `STATUS.md`, `logbook.md`
- `sync.bat`: naprawiona składnia `for /f` (backticki → `'git rev-parse HEAD'`)
- Ścieżki w narzędziach: `.ua/` → `output/` (build_graph, enrich, rewrite, stamp, update_tree)
- `test_kb.py`: odwołanie `best-you-kb.py` → `local-kb.py`

**Błędy napotkane:**
1. `ModuleNotFoundError: numpy` — `python` w PATH (hermes venv) bez numpy → rozwiązanie: anaconda3 python w `.bat`
2. `test_kb.py` FileNotFoundError — stara nazwa `best-you-kb.py` po rename → naprawione
3. `sync.bat` — zła składnia `for /f %%h in (\`git rev-parse HEAD\`)` → naprawione
4. `.gitignore` miał BOM (`\ufeff`) — działa, ale utrudnia parsowanie → czytane jako utf-8-sig

**Status:** ✅ Zakończone. Pipeline działa end-to-end.

---

## 2026-08-01 — Weryfikacje ad-hoc

**Co zrobiono:** Seria weryfikatorów tymczasowych (`%TEMP%\hermes-verify-*.py`) dla: rename, /model command, refactor notes/, ICM restructure (28 checków).

**Błędy napotkane:**
- Weryfikatory potrafiły fałszywie FAILOWAĆ (BOM, separatory ścieżek `/` vs `\`) — to były błędy weryfikatora, nie kodu. Wniosek: sprawdzaj u źródła prawdy (git check-ignore, realne uruchomienie), nie przez parsowanie tekstu.

**Status:** ✅ Zakończone. Weryfikatory usunięte.
