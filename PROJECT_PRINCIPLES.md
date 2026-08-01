# Zasady Pracy z Agentem AI w tym Projekcie

Ten dokument definiuje metodologię pracy nad tym projektem, opierając się na współpracy człowiek-AI. Celem jest przejście z roli "programisty" do "architekta systemu", gdzie człowiek definiuje strukturę, a AI wykonuje zadania w jej ramach.

## Kluczowe Zasady i Struktura

1.  **Architektura jako Kontekst (Metodologia ICM):**
    *   Struktura folderów jest traktowana jako architektura dla agenta.
    *   Kolejne etapy pracy są odzwierciedlane w ponumerowanych folderach (np. `01_research`, `02_build`), aby zapewnić sekwencyjny i przewidywalny przepływ pracy.

2.  **`AGENTS.md` jako Mapa Projektu:**
    *   Ten plik (już istnieje) jest głównym źródłem wiedzy dla agenta.
    *   Zawiera informacje o strukturze projektu, konwencjach nazewnictwa, sposobie uruchamiania testów i używanych bibliotekach. Agent musi go przeczytać na początku każdej sesji.

3.  **Tożsamość Agenta (`IDENTITY.md`):**
    *   Definiuje, kim jest agent (np. "Jesteś seniorem backendu w Pythonie"), jakie ma standardy jakości i jakich zachowań ma unikać. Ten plik określa "duszę" i styl pracy agenta.

4.  **Ciągłość Pracy (`STATUS.md`):**
    *   Ponieważ agent traci pamięć między sesjami, ten plik służy do śledzenia postępów.
    *   Po każdej sesji agent zapisuje, co zostało zrobione, jakie napotkano problemy i co jest następnym zadaniem.

5.  **Bramki Rewizyjne (Human Review Gates):**
    *   Agent nie może samodzielnie przechodzić do kolejnych, kluczowych etapów (np. od projektowania do implementacji).
    *   Wyniki każdej fazy muszą zostać zapisane w folderze `output/` i zatwierdzone przez człowieka przed rozpoczęciem następnego kroku.

6.  **Tryb Planowania:**
    *   Przed wykonaniem złożonego zadania (np. napisaniem nowego modułu), agent musi najpierw przedstawić plan działania w formie listy punktów. Plan wymaga akceptacji.

7.  **Dzielenie Zadań (Chunking):**
    *   Duże zadania są dzielone na mniejsze, atomowe części. Zamiast "zbuduj aplikację", polecenia powinny brzmieć "zaprojektuj schemat bazy danych", a następnie "zaimplementuj moduł X".

8.  **Zasada 60/30/10:**
    *   **60%** pracy to deterministyczny kod i skrypty (operacje na plikach, obliczenia).
    *   **30%** to automatyzacja oparta na prostych regułach.
    *   **Tylko 10%** to zadania dla AI (kreatywna logika, synteza, refaktoryzacja), gdzie jej elastyczność jest największą wartością.

9.  **Logbook (`logbook.md`):**
    *   Po każdym znaczącym zadaniu agent dopisuje krótką notatkę do logu: co zrobił, jakie błędy napotkał i jaki jest aktualny status. Umożliwia to audyt i śledzenie "procesu myślowego" agenta.

10. **Instrukcje Negatywne:**
    *   W plikach `AGENTS.md` lub `IDENTITY.md` jasno określamy, czego AI ma **NIE** robić (np. "nie używaj biblioteki X", "nie pisz testów jednostkowych dla prostych getterów"). Oszczędza to czas na poprawki.
