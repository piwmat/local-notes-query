# verification-skill.md — Protokół Pętli Weryfikacji

Ten plik opisuje **jak** wykonywać iteracyjną pętlę naprawczą w tym workspace.
`IDENTITY.md` mówi *kim jesteś* (audytor); ten plik mówi *jak działa cykl*.

## Cykl (jedna iteracja)

```
1. NAPISZ / ZMIEŃ   — minimalna zmiana kodu/parametru realizująca cel iteracji
2. URUCHOM          — realne wykonanie skryptu (nie "powinno działać")
3. ZWERYFIKUJ        — deterministyczny sędzia (skrypt/test) daje jednoznaczny wynik liczbowy lub tak/nie
4. PORÓWNAJ          — wynik vs poprzednia iteracja i vs cel
5a. POPRAWA → zapisz wynik, zaktualizuj STATUS.md, idź do kroku 1 (jeśli cel nieosiągnięty)
5b. BRAK POPRAWY → cofnij zmianę (git checkout / przywróć parametr), zwiększ licznik nieudanych prób
5c. LICZNIK NIEUDANYCH PRÓB == LIMIT → STOP. Nie zgaduj dalej. Patrz "Dead Man's Switch".
```

## Sędzia musi być deterministyczny

Nie oceniaj sukcesu przez wrażenie "chyba działa". Sędzia to skrypt zwracający
jedno- lub dwuwartościowy wynik, np.:

- `programs/eval_retrieval.py` → `Recall@10 = X.XXX`, `MRR = X.XXX`
- exit code skryptu (0 = OK, ≠0 = fail)
- diff liczby błędów lintera/testów przed i po

Jeśli nie ma deterministycznego sędziego dla zadania — **napisz go najpierw**,
zanim zaczniesz pętlę. Bez sędziego pętla nie ma prawa się zapętlać (ryzyko
spalania tokenów bez postępu, patrz Dead Man's Switch).

## Dead Man's Switch (twardy stop)

- **Limit domyślny: 3 kolejne nieudane próby** (brak poprawy metryki celu) w jednej sesji pętli.
- Po osiągnięciu limitu: **PRZERWIJ pętlę natychmiast.** Nie zaczynaj 4. próby.
- Napisz raport do `logbook.md`: co próbowano, jakie wyniki, hipoteza dlaczego nie działa.
- Zaktualizuj `STATUS.md` → pole `pętla_licznik` wyzeruj i opisz w sekcji "Otwarte pytania".
- To NIE jest porażka do ukrycia. Negatywny wynik = wynik (patrz precedens: A/B cognee, 2026-08-01).

## Logowanie blokerów (podczas pętli, nie tylko na końcu)

Każdy napotkany bloker w trakcie iteracji — zapisz od razu, krótko, w formie:

```
[iteracja N] próba: <co zmieniono> → wynik: <metryka> → wniosek: <1 zdanie>
```

Zbiorczy wpis do `logbook.md` po zakończeniu całej sesji pętli (sukces lub stop),
nie po każdej pojedynczej iteracji — unikamy zaśmiecania logu.

## Kiedy używać pętli, a kiedy nie

**Używaj**, gdy zadanie ma: (a) jasny cel liczbowy lub tak/nie, (b) deterministycznego
sędziego, (c) przestrzeń parametrów/zmian do przeszukania.

Przykład w tym repo: tuning `CONCEPT_DECAY` / `GRAPH_DECAY` w `local-kb.py` względem
`Recall@10` z `eval_retrieval.py`.

**Nie używaj**, gdy zadanie jest jednorazowe, strukturalne (zmiana architektury,
migracja plików) lub wymaga osądu jakościowego bez metryki — tam obowiązuje zwykła
bramka ludzka z `AGENTS.md`, nie pętla.

## Skrypt-sędzia dla tego repo

`programs/loop_tune.py` — implementuje powyższy cykl dla parametrów retrievalu
(`CONCEPT_DECAY`, `GRAPH_DECAY`). Patrz plik po szczegóły użycia.
