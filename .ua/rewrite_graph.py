import json, datetime, pathlib
root = pathlib.Path(r'C:\Users\Mateusz\Desktop\Notes\best you')
path = root/'.ua/knowledge-graph.json'
g = json.loads(path.read_text(encoding='utf-8'))

def fid(p): return f'file:{p}'
def rid(p): return f'resource:{p}'
def sid(p): return f'service:{p}'
def cid(p): return f'config:{p}'

old = {n['id']: n for n in g['nodes']}

# remove: build-embeddings, query, kb-cognee, .bat launchers, embeddings.json, tree-index.md resource (still referenced but now internal-only)
rm_ids = {
    fid('programs/query'),
    fid('programs/build-embeddings'),
    fid('programs/kb-cognee'),
    fid('programs/query.bat'),
    fid('programs/kb-cognee.bat'),
    fid('programs/update_index.bat'),
    fid('AGENTS.md'),
    cid('programs/build-embeddings'),
    sid('smart-connections-mcp'),
    rid('.smart-env/multi/*.ajson'),
    rid('embeddings.json'),
}
# upsert: best-you-kb.py
new_nodes = [n for n in g['nodes'] if n['id'] not in rm_ids]
new_nodes.append({
    'id': fid('programs/best-you-kb.py'),
    'type': 'file',
    'name': 'best-you-kb.py',
    'filePath': 'programs/best-you-kb.py',
    'summary': 'Independent hybrid RAG (~160 lines, 1 file, 0 deps beyond numpy/onnxruntime/tokenizers). ONNX embed query (bge-micro-v2, 384d) + in-process TF-IDF keyword (BM25-flavored) + MMR dedup (lam=0.75, gate 0.92, 6k token cap) + OpenAI-compatible LLM stream. Caches note vecs in-process at startup (no embeddings.json).',
    'tags': ['pipeline','rag','repl','independent'],
    'complexity': 'moderate',
})
# AGENTS.md is still relevant but no longer the architectural entry; replace id with new doc name
new_nodes.append({
    'id': fid('AGENTS.md'),
    'type': 'file',
    'name': 'AGENTS.md',
    'filePath': 'AGENTS.md',
    'summary': 'Agent Standard: opisuje best-you-kb.py pipeline. 0 deps poza stdlib + numpy/onnxruntime/tokenizers. Embedding notatek generowany in-process przez ONNX (nie potrzeba Smart Connections).',
    'tags': ['docs'],
    'complexity': 'simple',
})
# add config for best-you-kb
new_nodes.append({
    'id': cid('programs/best-you-kb.py'),
    'type': 'config',
    'name': 'best-you-kb.py env',
    'filePath': 'programs/best-you-kb.py',
    'summary': 'Env: LLM_BASE (default http://localhost:20128/v1), LLM_API_KEY, LLM_MODEL, plus constants TOP_VEC=10, TOP_KW=8, LAM=0.75, DUP_THRESH=0.92, TOKEN_BUDGET=6000.',
    'tags': ['config'],
    'complexity': 'simple',
})
g['nodes'] = new_nodes

# rebuild edges
edges = []
def link(src, tgt, type_, direction='forward', weight=0.5):
    edges.append({'source': src,'target': tgt,'type': type_,'direction': direction,'weight': weight})

KB = fid('programs/best-you-kb.py')
UT = fid('programs/update_tree.py')
TI = rid('programs/tree-index.md')
EMB = sid('bge-micro-v2')
KB_CFG = cid('programs/best-you-kb.py')

link(KB, EMB, 'depends_on')
link(KB, KB_CFG, 'configures')
link(KB, TI, 'reads_from', weight=0.6)
link(UT, TI, 'writes_to', weight=0.8)

g['edges'] = edges
g['layers'] = [
    {'id':'L0','name':'Entrypoints','description':'Single-file REPL','nodeIds':[KB]},
    {'id':'L1','name':'Pipeline','description':'Embed query (ONNX) + TF-IDF keyword + MMR + LLM','nodeIds':[KB, KB_CFG]},
    {'id':'L2','name':'Index','description':'tree-index.md (wikilinks)','nodeIds':[TI, UT]},
    {'id':'L3','name':'External services','description':'OpenAI-compatible LLM endpoint + ONNX embedder','nodeIds':[EMB]},
]
g['tourSteps'] = [
    {'order':1,'title':'1. REPL: best-you-kb.py','description':'user pytanie','nodeIds':[KB]},
    {'order':2,'title':'2. In-process note cache','description':'boot: load *.md, embed title+branch via bge-micro-v2 (~1-2s one-off)','nodeIds':[KB, EMB]},
    {'order':3,'title':'3. ONNX embed query','description':'bge-micro-v2 384-dim, ~5-20ms CPU','nodeIds':[EMB]},
    {'order':4,'title':'4. Vector top-10 (cosine)','description':'deterministic, vs in-memory vecs','nodeIds':[KB]},
    {'order':5,'title':'5. TF-IDF top-8 (BM25-ish)','description':'in-process, zero deps','nodeIds':[KB]},
    {'order':6,'title':'6. MMR select','description':'lam=0.75, dupe 0.92, 6k cap','nodeIds':[KB]},
    {'order':7,'title':'7. tree-index.md ancestor chain','description':'context header','nodeIds':[TI]},
    {'order':8,'title':'8. LLM synteza','description':'OpenAI-compatible stream','nodeIds':[KB, KB_CFG]},
    {'order':9,'title':'9. Reindex: update_tree.py','description':'wikilinks -> tree-index.md','nodeIds':[UT, TI]},
]
g['project']['description'] = 'best you/ - niezależny lokalny RAG (1 plik best-you-kb.py, 0 zewn. zależności, ONNX embed in-process + TF-IDF keyword + MMR + LLM). Plugin Smart Connections NIE jest wymagany do retrieval.'
g['project']['frameworks'] = ['numpy','onnxruntime','tokenizers']

path.write_text(json.dumps(g, ensure_ascii=False, indent=2), encoding='utf-8')
print('rewritten: nodes=' + str(len(g['nodes'])) + ' edges=' + str(len(g['edges'])))
