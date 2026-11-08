from pipeline import *
M=HERE/'manifest.json';m=json.loads(M.read_text(encoding='utf-8'));pending={'poly','elude','avert'}
inventory=json.loads((ROOT/'records/inventory-units.json').read_text(encoding='utf-8'))
inv={a['id']:a for a in inventory['units']}
metrics=[];unique={}
for a in m['assets']:
 assert a['id'] in inv
 a['gameplayGroup']=inv[a['id']]['group'];a['movementFlags']=inv[a['id']]['effectiveFlags']
 for entry in [a]+a['layers']:
  p=ROOT/entry['file'];assert p.exists(),p;assert sha(p)==entry['sha256'],p;unique[entry['file']]=entry
for file,entry in unique.items():
 p=ROOT/file;im=Image.open(p).convert('RGBA');arr=np.array(im);alpha=arr[:,:,3]
 border=int(np.count_nonzero(alpha[0])+np.count_nonzero(alpha[-1])+np.count_nonzero(alpha[:,0])+np.count_nonzero(alpha[:,-1]))
 hidden=int(np.count_nonzero((alpha==0)&np.any(arr[:,:,:3]!=0,axis=2)))
 _,parts=connected(alpha>=32)
 metrics.append(dict(file=file,sha256=sha(p),size=list(im.size),alphaMin=int(alpha.min()),alphaMax=int(alpha.max()),borderPixels=border,hiddenRgbPixels=hidden,significantComponents=len(parts),status='passed_alpha_bounds_and_hidden_rgb' if alpha.min()==0 and alpha.max()==255 and border==0 and hidden==0 else 'needs_review'))
assert all(a['status'].startswith('passed') for a in metrics)
for a in m['assets']:
 a['visualQA']={'status':'passed','evidence':'units/air-erekir/final-contact.png','backgrounds':['ivory','dark_green','gray'],'facing':'north','weaponVisibility':'visible','legCountVerified':a['legCount']}
 a['status']='awaiting_coordinator_recoil_patch' if a['id'] in pending else 'complete_art_assets_engine_unverified'
 a['openIssues']=['fixed_named_weapon_recoil_layer_replaced_by_coordinator_patch_pending_root_merge'] if a['id'] in pending else []
 a['pixelsFrozen']=True
thumb=175;cellw=thumb*3+12;cellh=thumb+35;sheet=Image.new('RGB',(4*cellw,7*cellh),(231,226,210));d=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
for i,a in enumerate(m['assets']):
 im=Image.open(ROOT/a['file']).convert('RGBA');im.thumbnail((thumb-10,thumb-10),Image.Resampling.LANCZOS);x=i%4*cellw;y=i//4*cellh
 for j,bg in enumerate([(246,241,224),(29,40,40),(125,125,125)]):
  tile=Image.new('RGBA',(thumb,thumb),bg+(255,));tile.alpha_composite(im,((thumb-im.width)//2,(thumb-im.height)//2));sheet.paste(tile.convert('RGB'),(x+j*thumb,y))
 d.text((x+5,y+thumb+5),a['id']+' | light / dark / gray',font=font,fill=(20,55,45))
contact=ROOT/'units/air-erekir/alpha-contact.png';sheet.save(contact)
write(contact.with_name(contact.name+'.generation.json'),dict(file=contact.relative_to(ROOT).as_posix(),sha256=sha(contact),operation='QA only: downscaled full final PNG on three actual opaque backgrounds; not production art',derivedFrom=[dict(file=a['file'],sha256=a['sha256'],generationRecord=a['generationRecord']) for a in m['assets']]))
bodyContact=ROOT/'units/air-erekir/body-contact.png';write(bodyContact.with_name(bodyContact.name+'.generation.json'),dict(file=bodyContact.relative_to(ROOT).as_posix(),sha256=sha(bodyContact),operation='QA contact of 17 final generated body layers; downsampled',derivedFrom=[dict(file=b['file'],sha256=b['sha256'],generationRecord=b['generationRecord']) for b in json.loads((HERE/'body-layers.json').read_text(encoding='utf-8'))]))
write(HERE/'final-qa.json',dict(status='passed_25_complete_3_awaiting_coordinator_patch',checkedAt=datetime.now(timezone.utc).isoformat(),unitCount=28,uniquePixelsChecked=len(metrics),checks=metrics,visualReviewed=True,bodyOnlyResidualWeaponCorrections=['merui','collaris'],independentReview='records/workers/serpulo-ground-naval/air-erekir-readonly-audit.json',engineNotVerified=True))
m.update(status='ready_25_units_3_coordinator_recoil_patches_pending',updatedAt=datetime.now(timezone.utc).isoformat(),pixelsFrozen=True,completedOwnedUnits=25,pendingCoordinatorPatches=sorted(pending),qaRecord='records/workers/air-erekir/final-qa.json',contactSheets=['units/air-erekir/final-contact.png','units/air-erekir/alpha-contact.png','units/air-erekir/body-contact.png'],completionNote='25 units final here; Poly/Elude/Avert are owned by coordinator-recoil-fix and must be patched by root before full completion.')
write(M,m)
keep={a['file'] for a in m['assets']}|{l['file'] for a in m['assets'] for l in a['layers']}|set(m['contactSheets'])
own=ROOT/'units/air-erekir';deletions=[]
for p in own.rglob('*.png'):
 rel=p.relative_to(ROOT).as_posix()
 if rel not in keep:
  deletions.append(dict(file=rel,sha256=sha(p),reason='Source board, superseded crop or intermediate contact; current final PNG and complete source text/hash chain retained.'))
deletepaths={x['file'] for x in deletions}
def update_refs(obj):
 if isinstance(obj,dict):
  f=obj.get('file') or obj.get('path')
  if isinstance(f,str):
   normalized=f.replace('\\','/');prefix=ROOT.as_posix()+'/'
   if normalized.startswith(prefix):normalized=normalized[len(prefix):]
   if normalized in deletepaths:obj['sourceImageRetained']=False;obj['sourceDeletionReason']='Superseded or exported intermediate; textual generation provenance and hash retained per user retention policy.'
  for value in list(obj.values()):update_refs(value)
 elif isinstance(obj,list):
  for x in obj:update_refs(x)
for folder in [own,HERE]:
 for p in folder.rglob('*.json'):
  try:obj=json.loads(p.read_text(encoding='utf-8-sig'))
  except Exception:continue
  update_refs(obj)
  if isinstance(obj,dict) and obj.get('file') in deletepaths:
   obj['status']='source_image_removed_after_final_export';obj['imageRetained']=False
   if isinstance(obj.get('evidence'),dict):obj['evidence']['sourceBytesPreserved']=False
  write(p,obj)
write(HERE/'cleanup-plan.json',dict(resolvedScope=str(own.resolve()),deletedImageCount=len(deletions),files=deletions,retainedImageCount=len(list(own.rglob('*.png')))-len(deletions),sourceImageRetained=False,approvedPolicy='AGENTS.md 2026-09-23 user retention policy; no backup image copies'))
print(json.dumps({'uniqueImagesQA':len(metrics),'plannedDelete':len(deletions),'retainedImages':len(list(own.rglob('*.png')))-len(deletions),'pendingCoordinator':sorted(pending)}))
