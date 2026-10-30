from pathlib import Path
import json,hashlib,datetime
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
read=lambda f:json.loads((ROOT/f).read_text(encoding='utf-8-sig'))
def dump(f,d):(ROOT/f).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mp='records/workers/air-erekir/manifest.json';m=read(mp);patch=read('records/coordinator-recoil-fix/patch-manifest.json')
assert patch.get('readyToMerge') or patch['status'] in ['ready_to_merge','passed_art_patch_ready_for_merge']
ids={'poly','elude','avert'};assert {x['id'] for x in patch['assets']}==ids
old=[a for a in m['assets'] if a['id'] in ids];replacements={a['id']:a for a in patch['assets']}
for a in replacements.values():
 assert sha(ROOT/a['file'])==a['sha256']
 assert all(x=='fixed_named_weapon_recoil_layer_replaced_by_coordinator_patch_pending_root_merge' for x in a.get('openIssues',[]))
 a['resolvedByRootMerge']=a.get('openIssues',[]);a['openIssues']=[]
 assert any(l['role']=='weapon' for l in a['layers'])
 for l in a['layers']:assert (ROOT/l['file']).is_file()
m['assets']=[replacements.get(a['id'],a) for a in m['assets']]
assert len({a['id'] for a in m['assets']})==28
m.update(updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='all_28_unit_art_complete_engine_not_verified',completedOwnedUnits=28,pendingCoordinatorPatches=[],independentRedrawnBodies=20,completionNote='All 28 art entries complete; Poly/Elude/Avert independent recoil patch merged and visually reviewed by root.',recoilPatch='records/coordinator-recoil-fix/patch-manifest.json',rootMergedPatchSha256=sha(ROOT/'records/coordinator-recoil-fix/patch-manifest.json'))
dump(mp,m)
bodies=read('records/workers/air-erekir/body-layers.json')
bodies=[b for b in bodies if b['id'] not in ids]+[{**next(l for l in a['layers'] if l['role']=='body'),'id':a['id']} for a in patch['assets']]
dump('records/workers/air-erekir/body-layers.json',bodies)
merge=dict(mergedAt=m['updatedAt'],sourcePatch=m['recoilPatch'],patchSha256=m['rootMergedPatchSha256'],replacedIds=sorted(ids),oldEntries=old,newEntries=list(replacements.values()),rootVisualReview='Passed three rest/recoil contact images: intact body underpaint, independently visible matching weapons, clean light/dark alpha; official weapon instances and recoil retained.',runtimeIntegrationVerified=False)
dump('records/recoil-patch-merge.json',merge)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
def contact(file,body=False,full=False):
 cols=4 if full else 7;tw=780 if full else 270;th=270;cw=tw+20;ch=315;rows=(28+cols-1)//cols
 sheet=Image.new('RGB',(cols*cw,rows*ch),(235,229,213));d=ImageDraw.Draw(sheet);sources=[]
 for i,a in enumerate(m['assets']):
  f=next(l['file'] for l in a['layers'] if l['role'].startswith('body')) if body else a['file']
  im=Image.open(ROOT/f).convert('RGBA');sources.append(dict(file=f,sha256=sha(ROOT/f)));im.thumbnail((250 if full else 270,270),Image.Resampling.LANCZOS)
  tile=Image.new('RGBA',(tw,th));td=ImageDraw.Draw(tile)
  colors=[(244,239,222,255),(31,42,42,255),(124,124,124,255)]
  for k,c in enumerate(colors):td.rectangle((k*tw//3,0,(k+1)*tw//3-1,th),fill=c)
  for k in range(3 if full else 1):tile.alpha_composite(im,((k*260+(260-im.width)//2) if full else (tw-im.width)//2,(th-im.height)//2))
  x=i%cols*cw+10;y=i//cols*ch+10;sheet.paste(tile.convert('RGB'),(x,y));d.text((x,y+276),a['id'],font=font,fill=(20,60,50))
 sheet.save(ROOT/file);dump(file+'.derived.json',dict(file=file,sha256=sha(ROOT/file),operation='Downsampled final review contact of actual PNG alpha on light/dark/gray; not a new generation',sources=sources,actualModel=None,actualQuality=None,runtimeIntegrationVerified=False))
contact('units/air-erekir/final-contact.png');contact('units/air-erekir/alpha-contact.png',full=True);contact('units/air-erekir/body-contact.png',body=True)
retention=read('records/workers/air-erekir/retention-cleanup.json')
assert retention['actuallyDeletedImageCount']==0 and retention['deletionPending']
retention['requestedDeletionImageCount']=len(retention['files']);retention['deletedImageCount']=0;dump('records/workers/air-erekir/retention-cleanup.json',retention)
dump('records/package-exclusions.json',dict(reason='Automatic approval rejected prior cleanup of these exact local intermediate images; they remain locally and are omitted from the deliverable archive, preserving all text provenance.',source='records/workers/air-erekir/retention-cleanup.json',files=retention['files'],localDeletionExecuted=False))
print(json.dumps(dict(mergedIds=sorted(ids),unitCount=28,pendingLocalIntermediateCleanup=len(retention['files']))))
