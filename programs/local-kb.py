#!/usr/bin/env python
"""best-you-kb - independent hybrid RAG over "best you/" vault. Zero deps beyond numpy/onnxruntime/tokenizers."""
import os, sys, json, time, re, math, urllib.request, urllib.error
from pathlib import Path
import numpy as np
from tokenizers import Tokenizer
import onnxruntime as ort

VAULT = Path(r"C:\Users\Mateusz\Desktop\Notes\best you\notes")
SNAP = Path.home() / ".cache" / "hermes-embedder" / "models--TaylorAI--bge-micro-v2" / "snapshots"
SNAP_DIR = SNAP / [d for d in os.listdir(SNAP) if os.path.isdir(SNAP / d)][0]
TOKEN_BUDGET = 6000
DUP_THRESH = 0.92
LAM = 0.75
TOP_VEC = 10
TOP_KW = 8
INSTRUCT = VAULT / "instructions.md"
LLM_BASE = os.environ.get("LLM_BASE", "http://localhost:20128/v1")
LLM_KEY = os.environ.get("LLM_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "oc/ling-3.0-flash-free")
TOK = Tokenizer.from_file(str(SNAP_DIR / "tokenizer.json")); TOK.enable_truncation(max_length=512); TOK.enable_padding(pad_id=0, pad_token="[PAD]", length=512)
SESS = ort.InferenceSession(str(SNAP_DIR / "onnx" / "model_quantized.onnx"))

def embed(texts):
    if isinstance(texts, str): texts = [texts]
    enc = TOK.encode_batch(texts); ids = np.array([e.ids for e in enc], dtype=np.int64)
    mask = np.array([e.attention_mask for e in enc], dtype=np.int64); ttype = np.array([e.type_ids for e in enc], dtype=np.int64)
    last = SESS.run(None, {"input_ids": ids, "attention_mask": mask, "token_type_ids": ttype})[0]
    m3d = np.expand_dims(mask, axis=-1).astype(np.float32); pooled = (last * m3d).sum(1) / m3d.sum(1).clip(min=1e-9)
    n = np.linalg.norm(pooled, axis=1, keepdims=True); return pooled / n.clip(min=1e-9)

# â”€â”€ vault load + vector cache â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _title(p): return re.sub(r"^#+ ", "", p.splitlines()[0]).strip() if p else ""
def _branch(name, max_lines=2):
    out = []; n = 0
    for line in name.splitlines():
        if line.startswith("#"): continue
        out.append(line); n += 1
        if n >= max_lines: break
    return " ".join(out).strip()

NOTES = []
NOTE_VECS = []
NOTE_TITLES = []
NOTE_TXT = {}
for p in sorted(VAULT.glob("*.md")):
    txt = p.read_text(encoding="utf-8", errors="ignore")
    NOTES.append({"path": p.name, "title": _title(txt), "branch": _branch(txt)})
    NOTE_TXT[p.name] = txt
NOTE_VECS = embed([re.sub(r"\s+", " ", n["title"] + " " + n["branch"]) for n in NOTES]).astype(np.float32)
# --- wikilink graph (NEIGHBORS) ---
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
TITLE_TO_PATH = {n["title"].strip().lower(): n["path"] for n in NOTES}
def _resolve_link(t):
    k = t.strip().lower()
    if k in TITLE_TO_PATH: return TITLE_TO_PATH[k]
    if (k + ".md") in NOTE_TXT: return k + ".md"
    return None
NEIGHBORS = {n["path"]: set() for n in NOTES}
for n in NOTES:
    for m in WIKILINK_RE.finditer(NOTE_TXT[n["path"]]):
        dst = _resolve_link(m.group(1))
        if dst and dst != n["path"]:
            NEIGHBORS[n["path"]].add(dst)
            NEIGHBORS[dst].add(n["path"])  # bidirectional


# â”€â”€ TF-IDF keyword (30 lines) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
TOK_RE = re.compile(r"[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]{3,}", re.UNICODE)
STOP = {"i","a","w","z","o","u","na","do","od","po","ze","we","za","przed",
        "nie","gdy","już","dla","jak","czy","przy","ale","tym","też","więc",
        "jest","są","być","można","bardzo","wtedy","teraz","jeszcze","tylko",
        "jeśli","jego","jej","ich","ten","ta","to","te","tego","tych",
        "oraz","aby","bo","że","co","gdyż","jeżeli","taki","taka","tako",
        "się"}
DOC_TERMS = []; DF = {}
for n in NOTES:
    toks = [t.lower() for t in TOK_RE.findall(n["title"] + " " + n["branch"]) if t.lower() not in STOP]
    DOC_TERMS.append(toks)
    for t in set(toks): DF[t] = DF.get(t, 0) + 1
N_DOCS = max(1, len(NOTES))
IDF = {t: math.log((N_DOCS + 1) / (d + 1)) + 1 for t, d in DF.items()}

def kw_search(q, k=TOP_KW):
    qts = [t for t in TOK_RE.findall(q.lower()) if t in IDF]
    if not qts: return []
    scored = []
    for i, toks in enumerate(DOC_TERMS):
        if not toks: continue
        tf = {}
        for t in toks:
            if t in IDF: tf[t] = tf.get(t, 0) + 1
        s = sum(IDF.get(t, 0) * (tf.get(t, 0) / (tf.get(t, 0) + 0.5)) for t in qts)
        if s > 0: scored.append((NOTES[i]["path"], s))
    scored.sort(key=lambda x: -x[1])
    return scored[:k]

# â”€â”€ vector + MMR â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def vec_search(q, k=TOP_VEC):
    qv = embed(q)[0]; sims = NOTE_VECS @ qv
    idx = np.argsort(-sims)[:k]; return [(NOTES[i]["path"], float(sims[i])) for i in idx]

def mmr(cands, token_budget=TOKEN_BUDGET, lam=LAM):
    picked = []; used = 0; vecs = []
    idx_map = {n["path"]: i for i, n in enumerate(NOTES)}
    candidates = [(idx_map.get(p, -1), p, base) for p, base in cands if p in idx_map]
    for _ in range(len(candidates)):
        best = None; best_score = -1e9
        for ci, p, base in candidates:
            if ci < 0: continue
            v = NOTE_VECS[ci]
            tk = len(TOK.encode(NOTE_TXT[p]).ids)
            if used > 0 and any(float(v @ vp) > DUP_THRESH for vp in vecs): continue
            score = lam * base - (1 - lam) * (max((float(v @ vp) for vp in vecs), default=0.0))
            score -= 0.05 * (tk / 1000)
            if used + tk > token_budget: continue
            if score > best_score: best_score = score; best = (p, v, tk)
        if best is None: break
        p, v, tk = best
        picked.append((p, next(b for pp, b in cands if pp == p), tk))
        vecs.append(v); used += tk
        if used >= token_budget: break
    return picked

def NoteTxt(p):
    return NOTE_TXT.get(p, NOTE_TXT.get([k for k in NOTE_TXT if Path(k).name == p][0], ""))

# --- RRF + graph expansion ---
RRF_K = 60
GRAPH_DECAY = 0.5
SEED_VEC = 5
SEED_KW = 3

def rrf(vec_ranked, kw_ranked, k=RRF_K):
    scores = {}
    for r, p in enumerate(vec_ranked, 1):
        scores[p] = scores.get(p, 0.0) + 1.0 / (k + r)
    for r, p in enumerate(kw_ranked, 1):
        scores[p] = scores.get(p, 0.0) + 1.0 / (k + r)
    return scores

def candidates(q):
    vec = vec_search(q)                    # top-10 (path, sim)
    kw = kw_search(q)                      # top-8  (path, bm25)
    seeds = rrf([p for p,_ in vec[:SEED_VEC]], [p for p,_ in kw[:SEED_KW]])
    pool = dict(seeds)                     # seeds keep their RRF score
    for seed, s in seeds.items():
        for nb in NEIGHBORS.get(seed, ()):
            nb_score = s * GRAPH_DECAY
            pool[nb] = max(pool.get(nb, 0.0), nb_score)
    return [(p, v) for p, v in sorted(pool.items(), key=lambda x: -x[1])]

def context_for(q):
    cands = candidates(q)
    picked = mmr(cands)
    parts = [f"Q: {q}", "--- selected notes ---"]
    used = sum(t for _, _, t in picked)
    for p, s, t in picked:
        title = next(n["title"] for n in NOTES if n["path"] == p) or Path(p).stem
        parts.append(f"# {title}\n{NoteTxt(p)[:5000]}")
    parts.append(f"--- budget: {used}/{TOKEN_BUDGET} ---")
    return "\n\n".join(parts), [p for p, _, _ in picked]

# â”€â”€ LLM (OpenAI-compatible, stream) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
SYS = (INSTRUCT.read_text(encoding="utf-8") if INSTRUCT.exists() else "Answer using only the provided notes. Cite filenames.")

def ask(q):
    ctx, cited = context_for(q)
    body = json.dumps({"model": LLM_MODEL, "stream": True,
        "messages": [{"role": "system", "content": SYS}, {"role": "user", "content": f"{ctx}\n\nQuestion: {q}\nAnswer with citations [file.md]."}]}).encode()
    req = urllib.request.Request(LLM_BASE + "/chat/completions", data=body,
        headers={"Content-Type": "application/json", **({"Authorization": f"Bearer {LLM_KEY}"} if LLM_KEY else {})})
    print(f"\n[{', '.join(cited)}]\n")
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            for line in r:
                line = line.decode(errors="ignore").strip()
                if line.startswith("data: "):
                    d = line[6:].rstrip(",")
                    if d == "[DONE]": break
                    try: o = json.loads(d)
                    except Exception: continue
                    if "choices" in o:
                        chs = o.get("choices") or []
                        if not chs: continue
                        c = chs[0].get("delta", {}).get("content", "") or ""
                        if c: sys.stdout.write(c); sys.stdout.flush()
        print()
    except urllib.error.URLError as e: print(f"\n[LLM error: {e}]")

# â”€â”€ REPL â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "retrieve":
        q = sys.argv[2]
        k = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[3] == "--topk" else 10
        for i, (p, _, _) in enumerate(mmr(candidates(q))[:k], 1):
            print(f"{i}. {p}")
        sys.exit(0)

    print(f"loaded {len(NOTES)} notes from '{VAULT.name}'; vocab={len(IDF)}", flush=True)
    while True:
        try: q = input("\nlocal-kb> ").strip()
        except EOFError: break
        if not q: continue
        if q.startswith("/model"):
            parts = q.split(" ", 1)
            if len(parts) > 1 and parts[1].strip():
                LLM_MODEL = parts[1].strip()
                print(f"model set to: {LLM_MODEL}")
            else:
                print(f"current model: {LLM_MODEL}")
            continue
        if q == "/q": break
        if q == "/list": print("\n".join(f"- {n['path']}: {n['title']}" for n in NOTES)); continue
        t = time.monotonic(); ctx, cited = context_for(q); print(f"[{time.monotonic()-t:.2f}s, {len(cited)} files]")
        ask(q)
