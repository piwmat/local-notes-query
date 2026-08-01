@echo off
setlocal
cd /d "%~dp0\.."
echo [1/5] tree-index.md
python programs\update_tree.py
echo [2/5] knowledge-graph.json
python tools\build_graph.py
echo [3/5] layers + tour
python tools\enrich.py
echo [4/5] stamp hash
for /f %%h in ('git rev-parse HEAD') do set "HASH=%%h"
python -c "import json,datetime,pathlib; p=pathlib.Path(r'output\knowledge-graph.json'); g=json.loads(p.read_text(encoding='utf-8')); g['project']['gitCommitHash']='%HASH%'; g['project']['analyzedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat(); p.write_text(json.dumps(g,ensure_ascii=False,indent=2),encoding='utf-8'); print('hash='+'%HASH%')"
echo [5/5] concept graph (Cognee-lite)
python tools\build_concept_graph.py
git add -A
git commit -m "sync: graph + tree"
endlocal
