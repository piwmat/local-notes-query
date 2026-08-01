"""queries.json eval. Runs local-kb.py retrieve() against the benchmark
fixture and reports Recall@K + MRR. No LLM tokens — pure retrieval quality.

Usage:
    python programs/eval_retrieval.py [--k 10]
"""
import json, os, sys, argparse, subprocess, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUERIES = ROOT / "programs" / "queries.json"
KB = ROOT / "programs" / "local-kb.py"

def run_retrieve(q: str, k: int) -> list[str]:
    """Invoke local-kb.py retrieve command, parse top-K filenames."""
    py_exe = r"C:\Users\Mateusz\AppData\Local\anaconda3\python.exe"
    out = subprocess.run(
        [py_exe, str(KB), "retrieve", q, "--topk", str(k)],
        capture_output=True, text=True, cwd=ROOT,
    )
    if out.returncode != 0:
        raise RuntimeError(out.stderr)
    return re.findall(r"^\d+\.\s+(.+\.md)", out.stdout, re.MULTILINE)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=10)
    args = ap.parse_args()
    qs = json.loads(QUERIES.read_text(encoding="utf-8-sig"))
    recall_hits = rec_sum = mrr_sum = 0
    for i, it in enumerate(qs, 1):
        got = run_retrieve(it["question"], args.k)
        expected = set(it["expected_notes"])
        hits = sum(1 for e in expected if any(e in g for g in got))
        recall_hits += hits
        rec_sum += len(expected)
        # MRR: first rank where any expected appears
        rr = 0.0
        for rank, g in enumerate(got, 1):
            if any(e in g for e in expected):
                rr = 1.0 / rank
                break
        mrr_sum += rr
        print(f"[{i:2d}] hits={hits}/{len(expected)} MRR={rr:.2f} :: {it['question'][:60]}")
    n = len(qs)
    print(f"\nRecall@{args.k} = {recall_hits / rec_sum:.3f}  ({recall_hits}/{rec_sum})")
    print(f"MRR          = {mrr_sum / n:.3f}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
