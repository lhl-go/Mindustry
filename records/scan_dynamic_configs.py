"""Read fixed official sources to enumerate dynamic UI configuration builders."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from urllib.request import urlopen,Request
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[1]
tree=json.loads((ROOT/'records/reference-ui-sources/official-tree-v160.7.json').read_text(encoding='utf-8-sig'))
entries=tree.get('tree',tree)
paths=[e['path'] for e in entries if e['path'].endswith('.java') and (e['path'].startswith('core/src/mindustry/world/blocks/') or e['path'].startswith('core/src/mindustry/editor/data/'))]
dest=ROOT/'records/reference-dynamic-sources';dest.mkdir(exist_ok=True)
COMMIT='17012d61d9e4c3cbd9820d87e81c24495486ac53'
def fetch(path):
    out=dest/path.replace('/','__')
    if not out.exists():
        req=Request('https://raw.githubusercontent.com/Anuken/Mindustry/'+COMMIT+'/'+path,headers={'User-Agent':'Mindustry-art-inventory'})
        with urlopen(req,timeout=45) as response:out.write_bytes(response.read())
    text=out.read_text(encoding='utf-8')
    lines=text.splitlines();matches=[]
    for i,line in enumerate(lines):
        if re.search(r'\b(buildConfiguration|buildEditor|buildEdit|buildTable|edit)\s*\(',line):
            if 'public ' in line or 'protected ' in line:matches.append(dict(line=i+1,declaration=line.strip(),excerpt='\n'.join(lines[i:i+38])))
    return dict(path=path,file=str(out.relative_to(ROOT)).replace('\\','/'),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),matches=matches)
results=[];errors=[]
with ThreadPoolExecutor(max_workers=12) as pool:
    jobs={pool.submit(fetch,p):p for p in paths}
    for future in as_completed(jobs):
        try:results.append(future.result())
        except Exception as exc:errors.append(dict(path=jobs[future],error=str(exc)))
report=dict(commit=COMMIT,scannedFileCount=len(results),requestedFileCount=len(paths),errors=errors,
 builders=[r for r in sorted(results,key=lambda r:r['path']) if r['matches']],
 mapAssetTypes=[r for r in sorted(results,key=lambda r:r['path']) if '/editor/data/' in r['path']],
 runtimePlatformValidation='outside_static_artwork_validation')
(ROOT/'records/dynamic-configuration-source-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(scanned=len(results),errors=errors,builders=[dict(path=r['path'],methods=len(r['matches'])) for r in report['builders']]),ensure_ascii=True))
