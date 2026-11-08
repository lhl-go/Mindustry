from pathlib import Path
import json,urllib.request,hashlib,concurrent.futures,io,datetime
from PIL import Image
HERE=Path(__file__).resolve().parent
inv=json.loads((HERE/'inventory.json').read_text(encoding='utf-8'));commit=inv['sourceCommit']
def fetch(e):
 p=HERE/'reference'/e['officialPath'];p.parent.mkdir(parents=True,exist_ok=True)
 try:
  data=p.read_bytes() if p.exists() else urllib.request.urlopen('https://raw.githubusercontent.com/Anuken/Mindustry/'+commit+'/'+e['officialPath'],timeout=25).read()
  actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
  if actual!=e['gitBlobSha1']:raise ValueError('Git blob hash mismatch')
  with Image.open(io.BytesIO(data)) as im:size=list(im.size);mode=im.mode
  if not p.exists():p.write_bytes(data)
  return {'officialPath':e['officialPath'],'file':p.relative_to(HERE).as_posix(),'sha256':hashlib.sha256(data).hexdigest(),'size':size,'mode':mode,'gitBlobVerified':True}
 except Exception as ex:return {'officialPath':e['officialPath'],'error':str(ex)}
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:results=list(ex.map(fetch,inv['entries']))
index={r['officialPath']:r for r in results}
for e in inv['entries']:
 r=index[e['officialPath']]
 if 'error' not in r:e['originalSize']=r['size'];e['originalMode']=r['mode'];e['officialSource']=r
(HERE/'inventory.json').write_text(json.dumps(inv,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'count':len(results),'errors':[r for r in results if 'error' in r],'results':results}
(HERE/'records').mkdir(exist_ok=True)
(HERE/'records/official-source-fetch.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'downloaded':len(results)-len(report['errors']),'errors':report['errors']},ensure_ascii=False))
