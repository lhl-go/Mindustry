from pathlib import Path
import hashlib,json,datetime
here=Path(__file__).resolve().parent;repo=here.parents[2]
p=here/'records/preflight.json';old=json.loads(p.read_text(encoding='utf-8')) if p.exists() else {};files={}
for rel in ['AGENTS.md','config/image-generation.json','docs/IMAGE_MODEL_POLICY.md']:
 data=(repo/rel).read_bytes();h=hashlib.sha256(data).hexdigest();files[rel]=h
 if old.get('files',{}).get(rel)!=h: print(data.decode('utf-8-sig'))
 else: print(rel+': read; SHA256 unchanged from personally read content '+h)
p.write_text(json.dumps({'readAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':files},indent=2)+'\n',encoding='utf-8')
