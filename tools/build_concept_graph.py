#!/usr/bin/env python
"""build_concept_graph.py — Cognee-lite: 1x LLM batch over notes -> concept triples JSON.

Per-note plain chat completion (no instructor/JSON schema — 9Router rejects it).
Output: output/concept-graph.json  { "<note>.md": [["podmiot","czasownik","dopelnienie"], ...] }
Deterministic at query time: graph is cached; LLM only runs here.
"""
import json, re, sys, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTES_DIR = ROOT / "notes"
OUT = ROOT / "output" / "concept-graph.json"
LLM_BASE = "http://localhost:20128/v1"
MODEL = "gc/gemini-2.5-flash-lite"  # works: credentials on 9Router (patrz local-kb.bat)
MAX_NOTE_CHARS = 3000
MAX_TRIPLES = 12

SYSTEM = (
    "Jesteś ekstraktorem faktów. Z tekstu notatki wypisujesz fakty jako trójki "
    "(podmiot, czasownik, dopełnienie) w języku polskim, formy bazowe (lematy). "
    "Odpowiadaj WYŁĄCZNIE tablicą JSON, np. [['siła woli','wyczerpywać się','wysiłek'], ...]. "
    "Bez komentarzy, bez markdown, bez ```."
)

def call_llm(note_name: str, text: str) -> list:
    user = f"Notatka: {note_name}\n---\n{text[:MAX_NOTE_CHARS]}\n---\nWypisz maks. {MAX_TRIPLES} trójek."
    body = json.dumps({
        "model": MODEL, "temperature": 0.0, "max_tokens": 800, "stream": False,
        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
    }).encode()
    req = urllib.request.Request(LLM_BASE + "/chat/completions", data=body,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        data = json.loads(r.read().decode())
    content = data["choices"][0]["message"]["content"]
    # strip fences, take first JSON array
    content = re.sub(r"```(?:json)?", "", content).strip()
    m = re.search(r"\[.*\]", content, re.S)
    if not m:
        return []
    parsed = json.loads(m.group(0))
    return [[str(s).strip(), str(v).strip(), str(o).strip()]
            for s, v, o in parsed if isinstance(parsed, list)
            and isinstance(s, str) and isinstance(v, str) and isinstance(o, str)]

def main() -> int:
    notes = sorted(NOTES_DIR.glob("*.md"))
    print(f"notes: {len(notes)}; model: {MODEL}")
    graph = {}
    fail = []
    t0 = time.monotonic()
    for i, p in enumerate(notes, 1):
        txt = p.read_text(encoding="utf-8", errors="ignore")
        triples = []
        for attempt in (1, 2):
            try:
                triples = call_llm(p.name, txt)
                break
            except (urllib.error.URLError, json.JSONDecodeError, KeyError, IndexError, ValueError) as e:
                print(f"  [{i}] {p.name}: attempt {attempt} fail ({type(e).__name__})", flush=True)
                time.sleep(3)
        if not triples:
            fail.append(p.name)
        graph[p.name] = triples
        print(f"  [{i}/{len(notes)}] {p.name}: {len(triples)} triples", flush=True)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(graph, ensure_ascii=False, indent=1), encoding="utf-8")
    total = sum(len(v) for v in graph.values())
    print(f"\nDONE: {len(notes)} notes, {total} triples, {len(fail)} empty -> {OUT}")
    print(f"time: {time.monotonic()-t0:.0f}s")
    if fail:
        print("EMPTY:", ", ".join(fail))
    return 0

if __name__ == "__main__":
    sys.exit(main())
