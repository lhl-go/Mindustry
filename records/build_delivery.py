"""Build a deterministic art manifest and browser catalog from verified local files."""
from pathlib import Path
from PIL import Image
import json,hashlib,datetime,shutil
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def dump(p,d):(ROOT/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def image_data(file):
 p=ROOT/file;im=Image.open(p);im.verify();im=Image.open(p)
 return dict(file=file,width=im.width,height=im.height,mode=im.mode,sha256=sha(p))
def incomplete_status(status):
 return any(t in str(status).lower() for t in ['in_progress','pending_review','pending_final','pending_visual','pending_coordinator','in_production','awaiting','blocked','needs_fix'])
inv=read('records/inventory-units.json');official={x['id']:x for x in inv['units']}
units=[];errors=[];workers=[];all_unit_files=set()
invalidation=read('records/render-invalidation.json') if (ROOT/'records/render-invalidation.json').exists() else {}
if invalidation.get('artCompletionBlockedUntilFinalCapture',True):errors.append('Final UI capture pending after source changes')
for worker in ['special','serpulo-ground-naval','air-erekir','root-builders']:
 manifest=f'records/workers/{worker}/manifest.json'
 if not (ROOT/manifest).exists():errors.append('Missing worker manifest: '+worker);continue
 m=read(manifest);workers.append(dict(file=manifest,sha256=sha(ROOT/manifest),status=m.get('status')))
 worker_status=str(m.get('status',''))
 if incomplete_status(worker_status):errors.append('Worker art production incomplete: '+worker+' / '+worker_status)
 for asset in m.get('assets',m.get('units',[])):
  uid=asset.get('id');file=asset.get('file') or asset.get('asset') or asset.get('compositePreview')
  if isinstance(file,dict):file=file.get('file')
  if uid not in official or not file:errors.append('Invalid unit entry '+str(uid));continue
  try:info=image_data(file)
  except Exception as e:errors.append(str(e));continue
  if info['mode']!='RGBA':errors.append('Non-RGBA unit '+uid)
  if asset.get('sha256') and asset['sha256']!=info['sha256']:errors.append('Worker SHA mismatch '+uid)
  asset_status=str(asset.get('status',''))
  if incomplete_status(asset_status):errors.append('Unit art incomplete: '+uid+' / '+asset_status)
  rec=asset.get('generationRecord') or (file+'.generation.json' if (ROOT/(file+'.generation.json')).exists() else file+'.derived.json')
  if not (ROOT/rec).exists():errors.append('Missing provenance '+uid)
  layers=asset.get('layers',asset.get('layerMapping',asset.get('layerFiles',[])))
  layer_files=[]
  if isinstance(layers,dict):layers=list(layers.values())
  for l in layers:
   f=l.get('file') if isinstance(l,dict) else l if isinstance(l,str) else None
   if isinstance(f,str) and (ROOT/f).is_file():layer_files.append(f)
  for l in asset.get('layerFiles',[]):
   f=l.get('file') if isinstance(l,dict) else l
   if isinstance(f,str) and (ROOT/f).is_file():layer_files.append(f)
  layer_files=sorted(set(layer_files or [file]));all_unit_files.update([file,*layer_files])
  units.append(dict(id=uid,name=official[uid].get('officialNameZhCN') or uid,family=official[uid]['family'],group=official[uid]['group'],**info,record=rec,workerManifest=manifest,sourceStatus=asset_status,layers=layer_files,layerCount=len(layer_files),runtimeIntegrationVerified=False))
required={u['id'] for u in inv['units'] if u['independentArtRequired']}
mapped=[u['id'] for u in units]
missing=sorted(required-set(mapped));duplicates=sorted({x for x in mapped if mapped.count(x)>1})
if missing:errors.append('Unmapped units: '+', '.join(missing))
if duplicates:errors.append('Duplicate units: '+', '.join(duplicates))
catalog=json.loads((ROOT/'ui/preview/data.js').read_text(encoding='utf-8').removeprefix('window.ART_DATA=').strip().rstrip(';'))
final_report=ROOT/'records/ui-render-all.json'
if not final_report.exists():errors.append('Missing final full UI capture report')
else:
 final=read('records/ui-render-all.json')
 for src in final.get('sources',[]):
  p=ROOT/src['file']
  if not p.exists() or sha(p)!=src['sha256']:errors.append('Stale final UI source: '+src['file'])
 if len(final.get('records',[]))!=sum(len(g['requiredDesignStates']) for g in catalog['groups'])*2:errors.append('Final UI capture coverage incomplete')
renders={};render_times={};render_reports=[]
for f in sorted((ROOT/'records').glob('ui-render-*.json')):
 r=json.loads(f.read_text(encoding='utf-8'));render_reports.append(f.relative_to(ROOT).as_posix())
 for item in r['records']:
  key=(item['group'],item['stateIndex'],item['device'])
  if r['createdAt']>=render_times.get(key,''):
   renders[key]=item;render_times[key]=r['createdAt']
 errors.extend('Render error: '+str(e) for e in r['errors'])
ui=[]
for g in catalog['groups']:
 states=[]
 for i,s in enumerate(g['requiredDesignStates']):
  r=renders.get((g['id'],i,'desktop'));mobile=renders.get((g['id'],i,'mobile'))
  if not r or not mobile:errors.append(f'Missing render check: {g["id"]} / {i}')
  for x in [r,mobile]:
   if x and (x['checks']['images'] or x['checks']['outsideControls'] or any(x['checks']['rootOverflow'])):errors.append('Failed render check '+x['query'])
  file=r.get('file') if r else None
  if file and not (ROOT/file).exists():errors.append('Missing state PNG '+file)
  states.append(dict(index=i,name=s,preview='ui/preview/index.html?id='+g['id']+'&state='+str(i),desktopPng=file,mobilePng=mobile.get('file') if mobile else None,renderChecksAvailable=bool(r and mobile)))
 ui.append(dict(id=g['id'],name=g['name'],kind=g['kind'],states=states,officialSources=g.get('officialSources',[]),implementation=['ui/preview/preview.js','ui/preview/screen-variants.js','ui/preview/dialog-component-variants.js']))
kit=[]
for x in read('ui/kit/manifest.json')['assets']:
 f=x['file'];kit.append(dict(name=Path(f).stem,**image_data(f),record=f+'.derived.json',borders=x.get('borderLeftBottomRightTop')))
concepts=[]
for f,name in [('ui/01-factory-defense-hud-v1.png','工厂防御 HUD 概念'),('ui/menu-network-research/01-main-menu-v1.png','主菜单'),('ui/menu-network-research/02-network-join-v1.png','联机'),('ui/menu-network-research/03-research-tree-v1.png','科技树'),('ui/menu-network-research/04-campaign-planet-v1.png','战役星球'),('ui/menu-network-research/05-map-editor-v1.png','地图编辑器')]:
 if (ROOT/f).exists():concepts.append(dict(name=name,**image_data(f),record=f+'.generation.json'))
data=dict(schemaVersion=1,createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='art_complete_runtime_unverified' if not errors else 'assembly_in_progress',version='v160.7',commit='17012d61d9e4c3cbd9820d87e81c24495486ac53',units=units,kit=kit,ui=ui,concepts=concepts,character=dict(**image_data('characters/02-alchemy-engineer-clean.png'),record='characters/02-alchemy-engineer-clean.png.derived.json'),workers=workers,renderReports=render_reports,validationErrors=errors,nonVisualUnits=[dict(id='block',mapping='Official internal block proxy; draws the associated building, no independent unit image.')],runtimeIntegrationVerified=False)
dump('exports/manifest.json',data)
(ROOT/'exports/delivery-data.js').write_text('window.DELIVERY_DATA='+json.dumps(data,ensure_ascii=False)+';\n',encoding='utf-8')
(ROOT/'ui/preview/unit-art-data.js').write_text('window.UNIT_ART_DATA='+json.dumps([dict(id=u['id'],name=u['name'],file=u['file']) for u in units],ensure_ascii=False)+';\n',encoding='utf-8')
dump('records/production-ledger.json',dict(updatedAt=data['createdAt'],status=data['status'],uiGroups=len(ui),baselineStateFamilies=281,additionalDynamicStateFamilies=27,totalStateFamilies=sum(len(x['states']) for x in ui),unitsRequired=len(required),unitArtMappings=len(units),missingUnits=missing,duplicates=duplicates,uniqueUnitPngFiles=len(all_unit_files),uiKitFiles=len(kit),conceptPages=len(concepts),characterCutouts=1,validationErrors=errors,manifest='exports/manifest.json',runtimeIntegrationVerified=False))
dump('records/progress.json',dict(updatedAt=data['createdAt'],scope='Complete Mindustry v160.7 UI and character/unit art package',status=data['status'],authoritativeLedger='records/production-ledger.json',deliveryEntry='exports/index.html',uiGroups=len(ui),unitArtMappings=len(units),unitMappingsRequired=68,runtimeIntegrationVerified=False,sharedGitTouched=False))
print(json.dumps(dict(status=data['status'],units=len(units),ui=len(ui),kit=len(kit),errors=errors),ensure_ascii=False))
