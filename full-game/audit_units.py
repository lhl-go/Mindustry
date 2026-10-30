import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
out=ROOT/'full-game/units';out.mkdir(exist_ok=True)
final_manifest=out/'manifest.json'
if final_manifest.exists():
    final=read(final_manifest)
    if final.get('status')=='complete_art_atlas_exports_engine_not_verified':
        errors=[]
        for asset in final['assets']:
            p=ROOT/asset['engineFile']
            if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=asset['engineSha256']:
                errors.append(asset['sourcePath'])
        print(json.dumps({'count':len(final['assets']),'mapped':len(final['assets'])-len(errors),'unmapped':errors,'manifest':'full-game/units/manifest.json','status':final['status']},ensure_ascii=False))
        raise SystemExit(1 if errors else 0)
inventory=[a for a in read(ROOT/'full-game/inventory-all-source-images.json')['assets']if a['owner']=='units-existing-audit']
mapping={};conflicts={}
def add(region,file,manifest,role='unknown'):
    if not file:return
    p=ROOT/file
    if not p.exists():return
    entry={'file':file,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'manifest':manifest,'role':role}
    if region in mapping and mapping[region]['file']!=file:
        conflicts.setdefault(region,[]).append(entry)
    else:mapping[region]=entry
workers=['records/workers/special/manifest.json','units/serpulo-ground-naval/manifest.json','records/workers/root-builders/manifest.json','records/workers/air-erekir/manifest.json','records/workers/air-erekir-parts/manifest.json','records/workers/serpulo-root-parts/manifest.json']
for name in workers:
    m=read(ROOT/name)
    for asset in m.get('assets',[]):
        maps=asset.get('layerMapping',{})
        if isinstance(maps,dict):
            for region,layers in maps.items():
                for l in layers:add(region,l['file'],name,l.get('role','unknown'))
        else:
            for l in maps:
                if l.get('engineRegion')and l.get('file'):add(l['engineRegion'],l['file'],name,l.get('role','unknown'))
        for l in asset.get('layers',[]):
            if isinstance(l,dict):
                region=l.get('officialRegion')or l.get('engineRegion')
                if not region and name=='records/workers/special/manifest.json':
                    region=asset['id'] if l.get('role')=='body' else Path(l['file']).stem
                if region and l.get('file'):add(region,l['file'],name,l.get('role','unknown'))
        if asset.get('officialRegion')and asset.get('file'):add(asset['officialRegion'],asset['file'],name,asset.get('role','unknown'))
        if asset.get('id')and asset.get('file')and not maps and not asset.get('layers'):
            add(asset['id'],asset['file'],name,asset.get('role','body'))
entries=[]
for a in inventory:
    region=Path(a['sourcePath']).stem
    entry={**a,'region':region,'mapping':mapping.get(region),'status':'mapped_existing_art'if region in mapping else 'requires_mapping'}
    entries.append(entry)
report={'schemaVersion':1,'status':'in_progress','count':len(entries),'mapped':sum(x['mapping']is not None for x in entries),'unmapped':[x['region']for x in entries if not x['mapping']],'mappingConflicts':conflicts,'assets':entries}
(out/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k]for k in ['count','mapped','unmapped']},ensure_ascii=False))
