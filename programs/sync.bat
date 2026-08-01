@echo off
setlocal
cd /d "%~dp0\.."
echo [1/4] tree-index.md
python programs\update_tree.py
echo [2/4] knowledge-graph.json
python tools\build_graph.py
echo [3/4] layers + tour
python tools\enrich.py
echo [4/4] stamp hash
for /f %%h in ('git rev-parse HEAD') do set "HASH=%%h"
python -c "import json,datetime,pathlib; p=pathlib.Path(r'output\knowledge-graph.json'); g=json.loads(p.read_text(encoding='utf-8')); g['project']['gitCommitHash']='%HASH%'; g['project']['analyzedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat(); p.write_text(json.dumps(g,ensure_ascii=False,indent=2),encoding='utf-8'); print('hash='+'%HASH%')"
git add -A
git commit -m "sync: graph + tree"
endlocal
