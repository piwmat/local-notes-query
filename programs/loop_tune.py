"""loop_tune.py — Pętla weryfikacji dla parametrów retrievalu (Recall@10).

Implementuje protokół z tools/verification-skill.md:
  1. zmień parametr (CONCEPT_DECAY lub GRAPH_DECAY) w local-kb.py
  2. uruchom eval_retrieval.py (deterministyczny sędzia)
  3. porównaj Recall@10 z poprzednią najlepszą wartością
  4a. poprawa -> zapisz jako nowy baseline, kontynuuj sweep
  4b. brak poprawy -> cofnij zmianę, +1 do licznika nieudanych prób
  5. licznik == LIMIT (domyślnie 3) kolejnych nieudanych prób -> STOP (Dead Man's Switch)

Nie commituje automatycznie do git — to zostaje jako bramka ludzka (AGENTS.md).
Na końcu drukuje raport do wklejenia w logbook.md i aktualizuje STATUS.md.

Usage:
    python programs/loop_tune.py [--param CONCEPT_DECAY] [--values 0.3,0.4,0.5,0.6,0.7] [--limit 3]
"""
import argparse
import re
import subprocess
import sys
import pathlib
import datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOCAL_KB = ROOT / "programs" / "local-kb.py"
EVAL = ROOT / "programs" / "eval_retrieval.py"
STATUS = ROOT / "STATUS.md"
PY_EXE = r"C:\Users\Mateusz\AppData\Local\anaconda3\python.exe"

RECALL_RE = re.compile(r"Recall@\d+\s*=\s*([\d.]+)")
MRR_RE = re.compile(r"MRR\s*=\s*([\d.]+)")


def read_param(name: str) -> float:
    txt = LOCAL_KB.read_text(encoding="utf-8")
    m = re.search(rf"^{name}\s*=\s*([\d.]+)", txt, re.MULTILINE)
    if not m:
        raise RuntimeError(f"nie znaleziono parametru {name} w local-kb.py")
    return float(m.group(1))


def write_param(name: str, value: float) -> None:
    txt = LOCAL_KB.read_text(encoding="utf-8")
    new_txt, n = re.subn(
        rf"^{name}\s*=\s*[\d.]+", f"{name} = {value}", txt, count=1, flags=re.MULTILINE
    )
    if n != 1:
        raise RuntimeError(f"nie udało się podmienić {name} (znaleziono {n} dopasowań)")
    LOCAL_KB.write_text(new_txt, encoding="utf-8")


def run_eval() -> tuple[float, float]:
    out = subprocess.run(
        [PY_EXE, str(EVAL)], capture_output=True, text=True, cwd=ROOT, timeout=600
    )
    if out.returncode != 0:
        raise RuntimeError(f"eval_retrieval.py zwrócił błąd:\n{out.stderr}")
    rm = RECALL_RE.search(out.stdout)
    mm = MRR_RE.search(out.stdout)
    if not rm or not mm:
        raise RuntimeError(f"nie udało się sparsować wyniku eval:\n{out.stdout}")
    return float(rm.group(1)), float(mm.group(1))


def update_status_counter(counter: str, cel: str, wynik: str) -> None:
    txt = STATUS.read_text(encoding="utf-8")
    txt = re.sub(r"- pętla_licznik: \S+", f"- pętla_licznik: {counter}", txt)
    txt = re.sub(r"- pętla_cel: .*", f"- pętla_cel: {cel}", txt)
    txt = re.sub(r"- pętla_ostatni_wynik: .*", f"- pętla_ostatni_wynik: {wynik}", txt)
    STATUS.write_text(txt, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--param", default="CONCEPT_DECAY", choices=["CONCEPT_DECAY", "GRAPH_DECAY"])
    ap.add_argument("--values", default="0.3,0.4,0.5,0.6,0.7")
    ap.add_argument("--limit", type=int, default=3, help="Dead Man's Switch: max kolejnych nieudanych prób")
    args = ap.parse_args()

    values = [float(v) for v in args.values.split(",")]
    param = args.param
    limit = args.limit

    if not LOCAL_KB.exists() or not EVAL.exists():
        print(f"[STOP] Brak wymaganych plików ({LOCAL_KB} / {EVAL}). Uruchamiaj z workspace 'best you'.")
        return 1

    original_value = read_param(param)
    print(f"[start] {param} baseline = {original_value}")

    print("[iteracja 0] pomiar baseline...")
    try:
        best_recall, best_mrr = run_eval()
    except Exception as e:
        print(f"[STOP] Baseline eval nie powiódł się: {e}")
        return 1
    best_value = original_value
    print(f"[iteracja 0] {param}={original_value} -> Recall@10={best_recall:.3f} MRR={best_mrr:.3f} (baseline)")

    baseline_recall = best_recall
    fail_streak = 0
    report_lines = [f"[iteracja 0] baseline {param}={original_value} -> Recall@10={best_recall:.3f} MRR={best_mrr:.3f}"]
    update_status_counter(f"0/{limit}", f"tuning {param} (cel: Recall@10 > 0.6)", f"baseline {best_recall:.3f}")

    stopped_early = False
    for i, v in enumerate(values, 1):
        if v == original_value:
            continue
        if fail_streak >= limit:
            stopped_early = True
            break

        write_param(param, v)
        try:
            recall, mrr = run_eval()
        except Exception as e:
            print(f"[iteracja {i}] {param}={v} -> BŁĄD WYKONANIA: {e}")
            write_param(param, best_value)  # rollback do najlepszego znanego stanu
            fail_streak += 1
            report_lines.append(f"[iteracja {i}] próba: {param}={v} -> błąd wykonania: {e} -> wniosek: cofnięto")
            update_status_counter(f"{fail_streak}/{limit}", f"tuning {param}", f"błąd przy {v}")
            continue

        if recall > best_recall:
            print(f"[iteracja {i}] {param}={v} -> Recall@10={recall:.3f} MRR={mrr:.3f}  ✅ POPRAWA (było {best_recall:.3f})")
            best_recall, best_mrr, best_value = recall, mrr, v
            fail_streak = 0
            report_lines.append(f"[iteracja {i}] próba: {param}={v} -> Recall@10={recall:.3f} MRR={mrr:.3f} -> wniosek: nowy najlepszy wynik")
        else:
            print(f"[iteracja {i}] {param}={v} -> Recall@10={recall:.3f} MRR={mrr:.3f}  ❌ brak poprawy (najlepszy: {best_recall:.3f} przy {best_value})")
            fail_streak += 1
            report_lines.append(f"[iteracja {i}] próba: {param}={v} -> Recall@10={recall:.3f} MRR={mrr:.3f} -> wniosek: gorzej/bez zmian ({fail_streak}/{limit})")

        update_status_counter(f"{fail_streak}/{limit}", f"tuning {param} (cel: Recall@10 > 0.6)", f"{best_recall:.3f} przy {param}={best_value}")

    # rollback do najlepszego znalezionego parametru (nie do oryginału, jeśli była poprawa)
    write_param(param, best_value)

    print()
    if stopped_early:
        print(f"[DEAD MAN'S SWITCH] Zatrzymano po {limit} kolejnych nieudanych próbach z rzędu.")
        report_lines.append(f"[STOP] Dead Man's Switch: {limit} nieudanych prób z rzędu. Zatrzymano pętlę.")
    print(f"[koniec] Najlepszy {param} = {best_value} -> Recall@10={best_recall:.3f} MRR={best_mrr:.3f} (baseline: {param}={original_value} -> Recall@10={baseline_recall:.3f})")

    if best_value != original_value:
        print(f"[UWAGA] Parametr {param} zapisany w local-kb.py jako {best_value} (zmiana z {original_value}).")
        print("        To wymaga akceptacji człowieka przed commitem (bramka ludzka, AGENTS.md).")
    else:
        print(f"[info] Brak poprawy względem baseline — {param} pozostaje {original_value}.")

    print("\n--- do wklejenia w logbook.md ---")
    today = datetime.date.today().isoformat()
    print(f"\n## {today} — Pętla tuningu {param}\n")
    print("**Co zrobiono:**")
    print(f"- Uruchomiono `loop_tune.py --param {param} --values {args.values} --limit {limit}`.")
    print("\n**Przebieg pętli:**")
    for line in report_lines:
        print(f"- {line}")
    print(f"\n**Wynik:** {param} {'zmieniony na ' + str(best_value) if best_value != original_value else 'bez zmian'} "
          f"(Recall@10: {baseline_recall:.3f} -> {best_recall:.3f}).")
    print(f"**Status:** {'⚠️ Zatrzymano Dead Man Switch — wymaga przeglądu.' if stopped_early else '✅ Zakończone.'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
