import json, datetime, pathlib, subprocess
path = pathlib.Path(r'C:\Users\Mateusz\Desktop\Notes\best you\.ua\knowledge-graph.json')
g = json.loads(path.read_text(encoding='utf-8'))
g['project']['gitCommitHash'] = '372f2b58d2621e9ca88c2f7aad2bc9bbbe3864b9'
g['project']['analyzedAt'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
path.write_text(json.dumps(g, ensure_ascii=False, indent=2), encoding='utf-8')
print('hash=' + '372f2b58d2621e9ca88c2f7aad2bc9bbbe3864b9')
