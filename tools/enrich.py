import json, datetime, pathlib
path = pathlib.Path(r'C:\Users\Mateusz\Desktop\Notes\best you\output\knowledge-graph.json')
g = json.loads(path.read_text(encoding='utf-8'))
n = {x['id']: x for x in g['nodes']}

def fid(p): return f'file:{p}'
def rid(p): return f'refile:{p}'  # placeholder; prawidlowe ids ponizej

# Popraw ids resources
fix = {}
for x in g['nodes']:
    if x['id'].startswith('refile:'):
        fix[x['id']] = 'resource:' + x['filePath']
for old, new in fix.items():
    x['id'] = new
    for e in g['edges']:
        if e['source'] == old: e['source'] = new
        if e['target'] == old: e['target'] = new
# deduplicate by id
seen = {}
for x in g['nodes']:
    seen.setdefault(x['id'], x)
g['nodes'] = list(seen.values())

# Layers
layers = [
    {'id':'L0','name':'Entrypoints','description':'REPL i launchers + agent standard','nodeIds':[fid('programs/query'),fid('programs/query.bat'),fid('AGENTS.md')]},
    {'id':'L1','name':'Pipeline scripts','description':'Core: ETL + query + indexer','nodeIds':[fid('programs/build-embeddings'),fid('programs/update_tree.py'),fid('programs/kb-cognee')]},
    {'id':'L2','name':'Data resources','description':'embeddings.json, tree-index.md, .smart-env/multi/.ajson','nodeIds':['resource:.smart-env/multi/*.ajson','resource:embeddings.json','resource:programs/tree-index.md']},
    {'id':'L3','name':'External services','description':'ONNX embedder + Smart Connections MCP','nodeIds':['service:bge-micro-v2','service:smart-connections-mcp']},
]
g['layers'] = layers

# Tour
tour = [
    {'order':1,'title':'1. Entry: REPL query','description':'user pytanie -> programs/query','nodeIds':[fid('programs/query')]},
    {'order':2,'title':'2. LLM config','description':'env LLM_BASE / LLM_MODEL','nodeIds':['config:programs/query']},
    {'order':3,'title':'3. ONNX embed query','description':'bge-micro-v2 384-dim','nodeIds':['service:bge-micro-v2']},
    {'order':4,'title':'4. Cosine vs embeddings.json','description':'top10 deterministic','nodeIds':['resource:embeddings.json']},
    {'order':5,'title':'5. Keyword MCP','description':'parallel Smart Connections MCP top8','nodeIds':['service:smart-connections-mcp']},
    {'order':6,'title':'6. MMR select','description':'lam=0.75, dupe 0.92, 6k cap','nodeIds':[fid('programs/query')]},
    {'order':7,'title':'7. Ancestor chain via tree-index.md','description':'context header','nodeIds':['resource:programs/tree-index.md']},
    {'order':8,'title':'8. ETL: build-embeddings','description':'.ajson -> embeddings.json (ETL out-of-band)','nodeIds':[fid('programs/build-embeddings'),'resource:.smart-env/multi/*.ajson','resource:embeddings.json']},
    {'order':9,'title':'9. Reindex: update_tree.py','description':'wikilinks -> tree-index.md','nodeIds':[fid('programs/update_tree.py'),'resource:programs/tree-index.md']},
    {'order':10,'title':'10. Experimental: Cognee backend','description':'kb-cognee (LanceDB+Kuzu), inactive','nodeIds':[fid('programs/kb-cognee')]},
]
g['tourSteps'] = tour

path.write_text(json.dumps(g, ensure_ascii=False, indent=2), encoding='utf-8')
print('layers=4 tour=10 -> ok')
