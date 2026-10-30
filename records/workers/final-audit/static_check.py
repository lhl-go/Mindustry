import json,re,hashlib,datetime
from pathlib import Path
from collections import defaultdict
import numpy as np
from PIL import Image
root=Path(r'D:\work\image\mindustry-image');out=root/'records/workers/final-audit';out.mkdir(parents=True,exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
raw=(root/'ui/preview/data.js').read_text(encoding='utf-8-sig');data=json.loads(re.sub(r';\s*$','',re.sub(r'^window\.ART_DATA\s*=\s*','',raw)))
groups=[g for g in data['groups'] if g['kind']=='screen'];dupes=[];missing=[];counts={};image_checks=[]
for g in groups:
 byhash=defaultdict(list)
 for n,state in enumerate(g['requiredDesignStates']):
  rel=f"ui/states/{g['id']}--s{n:02d}--desktop.png";p=root/rel
  if not p.exists():missing.append(rel);continue
  with Image.open(p) as im:dim=im.size;im.verify()
  h=sha(p);byhash[h].append({'stateIndex':n,'state':state,'file':rel})
  image_checks.append({'file':rel,'size':dim,'sha256':h})
 for h,items in byhash.items():
  if len(items)>1:dupes.append({'id':g['id'],'sha256':h,'states':items})
 counts[g['id']]=len(g['requiredDesignStates'])
dynamic=read(root/'records/dynamic-coverage.json');dynamic_summary={k:len(v) for k,v in dynamic.items() if isinstance(v,list)}
unit_checks=[];unit_errors=[];same_composite=[]
for worker in ['root-builders','special']:
 m=read(root/f'records/workers/{worker}/manifest.json')
 files=set()
 for a in m['assets']:
  files.add(a['file']);files.update(l['file'] for l in a.get('layers',[]))
  body=next((l['file'] for l in a.get('layers',[]) if l.get('role')=='body'),None)
  if body and body!=a['file'] and sha(root/body)==sha(root/a['file']):same_composite.append({'id':a['id'],'asset':a['file'],'body':body})
 for rel in sorted(files):
  p=root/rel;rp=next((p.with_name(p.name+s) for s in ['.generation.json','.derived.json'] if p.with_name(p.name+s).exists()),None)
  if not rp:unit_errors.append({'file':rel,'error':'missing sidecar'});continue
  r=read(rp);a=np.array(Image.open(p).convert('RGBA'));alpha=a[:,:,3];ys,xs=np.where(alpha>0);hidden=int(np.count_nonzero(np.any(a[:,:,:3]!=0,axis=2)&(alpha==0)))
  c={'file':rel,'shaMatches':sha(p)==r['sha256'],'size':[a.shape[1],a.shape[0]],'alphaExtrema':[int(alpha.min()),int(alpha.max())],'hiddenRgbPixels':hidden,'padding':min(int(xs.min()),int(ys.min()),a.shape[1]-int(xs.max())-1,a.shape[0]-int(ys.max())-1)}
  unit_checks.append(c)
  if not c['shaMatches'] or hidden or c['padding']<32:unit_errors.append(c)
manifest=read(root/'exports/manifest.json');export_ids=[u['id'] for u in manifest['units']]
known_ready=set(a['id'] for w in ['root-builders','special'] for a in read(root/f'records/workers/{w}/manifest.json')['assets'])
pngs=list((root/'ui/states').glob('*.png'));without_sidecars=[p.relative_to(root).as_posix() for p in pngs if not any(p.with_name(p.name+s).exists() for s in ['.generation.json','.derived.json'])]
result={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'screenGroups':len(groups),'screenStateCount':sum(counts.values()),'screenCounts':counts,'missingScreenPngs':missing,'samePixelScreenStates':dupes,'dynamicCoverageListCounts':dynamic_summary,'unitImageCountChecked':len(unit_checks),'unitErrors':unit_errors,'unitChecks':unit_checks,'compositesIdenticalToBody':same_composite,'exportStatus':manifest['status'],'exportUnitCount':len(export_ids),'knownReadyAbsentFromExport':sorted(known_ready-set(export_ids)),'uiStatePngCount':len(pngs),'uiStatePngsWithoutAdjacentSidecar':len(without_sidecars),'uiStateSourceRecordPolicy':'ui-render-*.json contains per-file records; adjacent sidecars not required by audit but README wording checked separately.','screenImageChecks':image_checks}
(out/'static-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['unitChecks','screenImageChecks']},ensure_ascii=False,indent=2))
