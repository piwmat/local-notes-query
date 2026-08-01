import json, datetime, pathlib
root = pathlib.Path(r'C:\Users\Mateusz\Desktop\Notes\best you')
vault = pathlib.Path(r'C:\Users\Mateusz\Desktop\Notes')

def nid(t, p): return f'{t}:{p}'

def file_node(p, name, summary, tags, complexity='moderate'):
    return {'id': nid('file', p),'type': 'file','name': name,'filePath': p,'summary': summary,'tags': tags,'complexity': complexity}

def data_node(p, name, summary, tags):
    return {'id': nid('resource', p),'type': 'resource','name': name,'filePath': p,'summary': summary,'tags': tags,'complexity': 'simple'}

def config_node(p, name, summary, tags):
    return {'id': nid('config', p),'type': 'config','name': name,'filePath': p,'summary': summary,'tags': tags,'complexity': 'simple'}

def service_node(p, name, summary, tags):
    return {'id': nid('service', p),'type': 'service','name': name,'filePath': p,'summary': summary,'tags': tags,'complexity': 'moderate'}

def edge(src, tgt, type_, direction='forward', weight=0.5):
    return {'source': src,'target': tgt,'type': type_,'direction': direction,'weight': weight}

nodes = []

# -- Data resources (sources of truth) --
nodes.append(data_node('.smart-env/multi/*.ajson','Smart Connections .ajson','Surowe embeddingi ze Smart Connections (cache per-source, JSONL)',['data','embeddings','source']))
nodes.append(data_node('embeddings.json','embeddings.json','Pre-computed 384-dim vectors (bge-micro-v2) per note z vault \"best you\"',['data','embeddings','derived']))
nodes.append(data_node('programs/tree-index.md','tree-index.md','Auto-generated knowledge tree (parent chain notes)',['data','index','derived']))

# -- Configs / env --
nodes.append(config_node('programs/query','programs/query config','Env: LLM_BASE=http://localhost:20128/v1, LLM_MODEL, constants: TOKEN_BUDGET=6000, DUP_THRESH=0.92, lam=0.75',['config','env']))
nodes.append(config_node('programs/build-embeddings','build-embeddings config','Hardcoded: VAULT, MULTI (.smart-env/multi), EXPECTED_DIM=384',['config']))
nodes.append(service_node('smart-connections-mcp','Smart Connections MCP','External Node.js MCP server: keyword search over Obsidian vault. Przegladane: C:/smart-connections-mcp/dist/index.js. Env: SMART_VAULT_PATH=Notes.',['external','mcp','keyword']))

# -- Pipeline scripts (files) --
nodes.append(file_node('programs/build-embeddings','build-embeddings','Stream-parses Smart Connections .ajson, filtrowane do \"best you/\" prefix, oczekuje 384-dim, zapisuje embeddings.json.',['pipeline','etl','extract']))
nodes.append(file_node('programs/query','query','REPL RAG. Pipeline: (1) ONNX embed query -> cosine top10 vs embeddings.json, (2) keyword_search via MCP top8, (3) MMR select (lam=0.75, dupe 0.92, 6k cap), (4) build context + ancestor chain, (5) OpenAI-compatible LLM synteza.',['pipeline','rag','repl']))
nodes.append(file_node('programs/update_tree.py','update_tree.py','Regeneruje tree-index.md z wikilinkow w vault.',['pipeline','index']))
nodes.append(file_node('programs/kb-cognee','kb-cognee','Experimentalny backend Cognee (nieaktywny). Dane w .cognee_* (LanceDB + Kuzu).',['pipeline','experimental']))
nodes.append(file_node('output/knowledge-graph.json','knowledge-graph.json','UA knowledge graph: dokumentuje ARCHEKTURE pipeline (ten plik).',['index','ua']))

# -- Launchers / wrappers --
nodes.append(file_node('programs/query.bat','query.bat','Win launcher: uruchamia programs/query.',['launcher']))
nodes.append(file_node('programs/kb-cognee.bat','kb-cognee.bat','Win launcher: uruchamia programs/kb-cognee.',['launcher']))
nodes.append(file_node('programs/update_index.bat','update_index.bat','Win launcher: update_tree.py.',['launcher']))
nodes.append(file_node('AGENTS.md','AGENTS.md','Agent Standard dla vaultu - opis pipeline + zasady.',['docs']))

# -- Embedder model (external cached) --
nodes.append(service_node('bge-micro-v2','bge-micro-v2 ONNX','ONNX runtime embedder (TaylorAI/bge-micro-v2, 384-dim), cache ~/.cache/hermes-embedder.',['model','onnx','embedder']))

# Build edges
edges = []
def link(src_id, tgt_id, type_, direction='forward', weight=0.5):
    edges.append({'source': src_id,'target': tgt_id,'type': type_,'direction': direction,'weight': weight})

R_AJ = nid('resource','.smart-env/multi/*.ajson')
R_EMB = nid('resource','embeddings.json')
R_TREE = nid('resource','programs/tree-index.md')
F_BE = nid('file','programs/build-embeddings')
F_Q = nid('file','programs/query')
F_UT = nid('file','programs/update_tree.py')
F_KB = nid('file','programs/kb-cognee')
S_MCP = nid('service','smart-connections-mcp')
S_BGE = nid('service','bge-micro-v2')
C_BE = nid('config','programs/build-embeddings')
C_Q = nid('config','programs/query')

# ETL
link(F_BE, R_AJ, 'reads_from', 'forward', 0.8)
link(F_BE, R_EMB, 'writes_to', 'forward', 0.8)
link(F_BE, C_BE, 'configures', 'forward', 0.6)
link(F_BE, S_BGE, 'depends_on', 'forward', 0.6)  # wymiar musi zgadzac sie z modelem

# Update tree
for n in [F_BE, F_Q, F_KB]:
    pass
link(F_UT, R_TREE, 'writes_to', 'forward', 0.8)
link(F_Q, R_TREE, 'reads_from', 'forward', 0.6)
link(F_Q, R_EMB, 'reads_from', 'forward', 0.8)
link(F_Q, S_MCP, 'subscribes', 'forward', 0.8)
link(F_Q, S_BGE, 'depends_on', 'forward', 0.7)
link(F_Q, C_Q, 'configures', 'forward', 0.6)
link(F_Q, F_KB, 'related', 'bidirectional', 0.5)

graph = {
    'version': '2.0.0',
    'kind': 'codebase',
    'project': {
        'name': 'best you',
        'languages': ['python'],
        'frameworks': ['onnxruntime','tokenizers','numpy'],
        'description': 'Lokalny RAG pipeline dla vaultu best you/. ONNX embeddings (bge-micro-v2) + Smart Connections MCP keyword + MMR dedup + LLM synteza (OpenAI-compatible). Wyodrebnione stage-y: extract (build-embeddings), index (update_tree.py), query (REPL). Eksperymentalny backend Cognee (kb-cognee).',
        'analyzedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'gitCommitHash': '',
    },
    'nodes': nodes,
    'edges': edges,
}
out = root/'output/knowledge-graph.json'
out.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'nodes={len(nodes)} edges={len(edges)} -> {out}')
