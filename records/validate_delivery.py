from pathlib import Path
from PIL import Image
import json,hashlib,datetime
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=read(ROOT/'exports/manifest.json');failures=[];checks=[];seen=set()
provenance_seen=set();provenance_checks=[]
def provenance(file,record_file=None,expected_sha=None):
 if record_file is None:
  record_file=next((file+s for s in ['.derived.json','.generation.json'] if (ROOT/(file+s)).is_file()),None)
 if not record_file or not (ROOT/record_file).is_file():failures.append('Missing image provenance '+file);return
 try:d=read(ROOT/record_file)
 except Exception as e:failures.append('Unreadable provenance '+record_file+': '+str(e));return
 expected_sha=expected_sha or (sha(ROOT/file) if (ROOT/file).is_file() else None)
 if expected_sha and d.get('sha256')!=expected_sha:failures.append('Provenance SHA mismatch '+record_file)
 if record_file in provenance_seen:return
 provenance_seen.add(record_file);provenance_checks.append(dict(file=record_file,sha256=sha(ROOT/record_file),imageRetained=(ROOT/file).is_file()))
 sources=d.get('derivedFrom',[])
 if isinstance(sources,dict):sources=[sources]
 for source in sources if isinstance(sources,list) else []:
  if not isinstance(source,dict):continue
  child=source.get('generationRecord') or source.get('record')
  sf=source.get('file')
  if child and sf:
   if not (ROOT/child).is_file() and (ROOT/record_file).parent.joinpath(child).is_file():child=(ROOT/record_file).parent.joinpath(child).relative_to(ROOT).as_posix()
   provenance(sf,child,source.get('sha256'))
def record(f,expected=None,transparent=False):
 if f in seen:return
 seen.add(f);p=(ROOT/f).resolve()
 if not p.is_relative_to(ROOT.resolve()) or not p.is_file():failures.append('Missing or external '+f);return
 try:
  im=Image.open(p);im.verify();im=Image.open(p);a=np.array(im)
  d=dict(file=f,sha256=sha(p),size=list(im.size),mode=im.mode)
  if expected and d['sha256']!=expected:failures.append('SHA mismatch '+f)
  if transparent:
   if im.mode!='RGBA':failures.append('Non-alpha asset '+f)
   else:
    alpha=im.getchannel('A');bbox=alpha.getbbox();d.update(alphaExtrema=list(alpha.getextrema()),alphaBounds=bbox,clearBorder=bool(not a[0,:,3].any() and not a[-1,:,3].any() and not a[:,0,3].any() and not a[:,-1,3].any()),hiddenRgbZero=bool((a[a[:,:,3]==0,:3]==0).all()))
    if not d['clearBorder'] or not bbox:failures.append('Invalid alpha border '+f)
  checks.append(d)
 except Exception as e:failures.append(f+': '+str(e))
for unit in manifest['units']:
 record(unit['file'],unit['sha256'],True)
 provenance(unit['file'],unit['record'],unit['sha256'])
 for layer in unit['layers']:
  record(layer,transparent=True);provenance(layer)
 if not (ROOT/unit['record']).is_file():failures.append('Missing source record '+unit['id'])
for x in manifest['kit']:
 record(x['file'],x['sha256'],not x['file'].endswith('factory-scene.png'));provenance(x['file'],x['record'],x['sha256'])
for x in manifest['concepts']:
 record(x['file'],x['sha256']);provenance(x['file'],x['record'],x['sha256'])
record(manifest['character']['file'],manifest['character']['sha256'],True)
provenance(manifest['character']['file'],manifest['character']['record'],manifest['character']['sha256'])
for g in manifest['ui']:
 for s in g['states']:
  for key in ['desktopPng','mobilePng']:
   if s.get(key):record(s[key])
  if not s['renderChecksAvailable']:failures.append('Unchecked UI state '+g['id']+'/'+str(s['index']))
required=json.loads((ROOT/'records/inventory-units.json').read_text(encoding='utf-8-sig'))['units']
expected={x['id'] for x in required if x['independentArtRequired']}
actual=[x['id'] for x in manifest['units']]
if set(actual)!=expected or len(actual)!=len(expected):failures.append('Unit coverage is incomplete or duplicated')
if len(manifest['ui'])!=64 or sum(len(x['states']) for x in manifest['ui'])!=308:failures.append('UI coverage incomplete')
if manifest['validationErrors']:failures+=manifest['validationErrors']
out=dict(checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Final physical art files, alpha boundary, hashes, required IDs, UI render evidence and recursive provenance records',imageCount=len(checks),unitCount=len(actual),uiGroups=len(manifest['ui']),stateFamilies=sum(len(x['states']) for x in manifest['ui']),passed=not failures,failures=failures,images=checks,provenanceRecords=provenance_checks,runtimeIntegrationVerified=False)
(ROOT/'records/final-delivery-verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:out[k] for k in ['passed','imageCount','unitCount','uiGroups','stateFamilies','failures']},ensure_ascii=False))
