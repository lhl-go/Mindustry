"""Authorized alpha cleanup, native cropping and assembly; no painted pixels created."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib, json, sys, copy
import numpy as np
from PIL import Image, ImageOps

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'units/coordinator-recoil-fix'
sys.path.insert(0,str(ROOT/'records'))
from pixel_tools import components
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rel=lambda p:Path(p).relative_to(ROOT).as_posix()
def write(p,data):Path(p).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=lambda:datetime.now(ZoneInfo('America/New_York')).isoformat()
src=OUT/'01-recoil-parts-v1.png'
arr=np.array(Image.open(src).convert('RGBA'))
parts=components(arr[:,:,3]>=16,min_area=500)
parts=sorted(parts,key=lambda c:-c['area'])[:6]
if len(parts)!=6:raise RuntimeError('Expected six isolated objects: '+str([(p['area'],p['bbox']) for p in parts]))
top=sorted(parts,key=lambda p:(p['bbox'][1]+p['bbox'][3])/2)[:3]
bottom=[p for p in parts if p not in top]
top.sort(key=lambda p:p['bbox'][0]);bottom.sort(key=lambda p:p['bbox'][0])
ids=['poly','elude','avert']
assets={}
for role,group in [('body',top),('weapon',bottom)]:
 for id,part in zip(ids,group):
  keep=np.zeros(arr.shape[:2],bool)
  for y,s,e in part['runs']:keep[y,s:e]=True
  pixels=arr.copy();alpha=np.clip(np.rint((arr[:,:,3].astype(float)-8)*255/237),0,255).astype(np.uint8)
  alpha[~keep]=0;pixels[:,:,3]=alpha;pixels[~keep,:3]=0
  box=part['bbox'];cut=Image.fromarray(pixels).crop(box)
  pad=32;im=Image.new('RGBA',(cut.width+2*pad,cut.height+2*pad),(0,0,0,0));im.alpha_composite(cut,(pad,pad))
  path=OUT/(id+'-'+role+'.png');im.save(path)
  rec=dict(schemaVersion=1,file=rel(path),sha256=sha(path),width=im.width,height=im.height,format='PNG',mode='RGBA',derivedAt=now(),
   derivedFrom=[dict(file=rel(src),sha256=sha(src),generationRecord=rel(src)+'.generation.json',nativeSize=[arr.shape[1],arr.shape[0]])],
   operation=dict(type='authorized_alpha_cleanup_crop_pad',alphaCutoff=16,componentSelection='one complete disconnected atlas object',sourceCropBox=box,padding=pad,resampling=False,redrawing=False,alphaRemap='clip(round((alpha-8)*255/237),0,255)',rgbPolicy='retained RGB unchanged; removed background RGB=0'),
   authorization='User explicitly authorized local alpha cleanup and slicing in production chat on 2026-10-26',actualModel=None,actualQuality=None,
   modelEvidence='Derived from the builtin generation record; exact model and quality undisclosed',validation=dict(realAlpha=True,alphaExtrema=list(im.getchannel('A').getextrema()),edgeAlphaNonzero=bool(np.array(im)[:1,:,3].any() or np.array(im)[-1:,:,3].any() or np.array(im)[:,:1,3].any() or np.array(im)[:,-1:,3].any()),visualReview='pending'))
  write(str(path)+'.derived.json',rec)
  assets[(id,role)]={'path':path,'image':im,'record':rec,'sourceComponentArea':part['area']}

old=json.loads((ROOT/'records/workers/air-erekir/manifest.json').read_text(encoding='utf-8-sig'))
old={a['id']:a for a in old['assets'] if a['id'] in ids}
evidence=json.loads((HERE/'source-evidence.json').read_text(encoding='utf-8-sig'))
evidence={u['id']:u for u in evidence['units']}
spec={
 'poly':dict(scale=.42,x=.29,y=.10,angle=0,count=2),
 'elude':dict(scale=.72,x=.19,y=-.10,angle=-35,count=2),
 'avert':dict(scale=.48,x=0,y=-.16,angle=0,count=1),
}
patch=[];diagnostics=[]
for id in ids:
 body=assets[(id,'body')];weapon=assets[(id,'weapon')];s=spec[id]
 # The native part masters remain unscaled. Downscaling here is only the documented static composition.
 wim=weapon['image'].resize((round(weapon['image'].width*s['scale']),round(weapon['image'].height*s['scale'])),Image.Resampling.LANCZOS)
 margin=160;size=(body['image'].width+margin*2,body['image'].height+margin*2)
 bodyOrigin=(margin,margin);center=(margin+body['image'].width/2,margin+body['image'].height/2)
 mounts=[]
 signs=[-1,1] if s['count']==2 else [0]
 for sign in signs:
  # Pixel poses are a separately declared art alignment estimate, not the canonical game-world offsets.
  angle=sign*s['angle'];mount=(center[0]+sign*body['image'].width*s['x'],center[1]+body['image'].height*s['y'])
  mounts.append(dict(mirrorX=sign<0,rotationDegrees=angle,anchorPixels=[round(mount[0],2),round(mount[1],2)]))
 def assemble(recoil):
  canvas=Image.new('RGBA',size,(0,0,0,0));canvas.alpha_composite(body['image'],bodyOrigin)
  for mount in mounts:
   wi=ImageOps.mirror(wim) if mount['mirrorX'] else wim
   wi=wi.rotate(mount['rotationDegrees'],Image.Resampling.BICUBIC,expand=True)
   # Recoil mock shifts the weapon only; the underlying continuous armor remains unchanged.
   px=int(round(mount['anchorPixels'][0]-wi.width/2));py=int(round(mount['anchorPixels'][1]-wi.height*.78+recoil))
   canvas.alpha_composite(wi,(px,py))
  return canvas
 rest=assemble(0);recoiled=assemble(16)
 restpath=OUT/(id+'-assembled.png');rest.save(restpath)
 sources=[dict(file=rel(x['path']),sha256=sha(x['path']),record=rel(x['path'])+'.derived.json') for x in (body,weapon)]
 restRec=dict(schemaVersion=1,file=rel(restpath),sha256=sha(restpath),width=rest.width,height=rest.height,format='PNG',mode='RGBA',derivedAt=now(),derivedFrom=sources,
  operation=dict(type='documented_static_layer_composition',bodyOriginPixels=bodyOrigin,weaponScale=s['scale'],weaponInstances=mounts,weaponPivotNormalized=[.5,.78],pixelAlignment='estimated_art_alignment; not runtime verified',canonicalSourceCoordinates='preserved separately in patch asset officialWeaponOffsets; never replaced by pixels',newPaint=False),
  actualModel=None,actualQuality=None,modelEvidence='Derived parts inherit generation evidence',runtimeIntegrationVerified=False)
 write(str(restpath)+'.derived.json',restRec)
 row=copy.deepcopy(old[id]);row.update(file=rel(restpath),generationRecord=rel(restpath)+'.derived.json',sha256=sha(restpath),size=list(rest.size),compositePreview=rel(restpath),status='art_complete_engine_not_verified',engineNotVerified=True,
   bodyAnchorPixels=[round(center[0],2),round(center[1],2)],recoilArtRepaired=True,recoilSourceEvidence='records/coordinator-recoil-fix/source-evidence.json')
 row['layers']=[]
 for role,a in [('body',body),('weapon',weapon)]:
  row['layers'].append(dict(id=id+('-weapon' if role=='weapon' else ''),file=rel(a['path']),role=role,generationRecord=rel(a['path'])+'.derived.json',sha256=sha(a['path']),size=list(a['image'].size),anchorNormalized=[.5,.5] if role=='body' else [.5,.78],facing='north',completeUnderpaint=True,pixelAnchorEvidence='estimated_art_alignment; runtime not verified'))
 row['layerFiles']=[r['file'] for r in row['layers']]
 row['layerMapping']=[dict(engineRegion=id,file=row['layers'][0]['file'],role='body',reuse=False),dict(engineRegion=id+'-weapon',file=row['layers'][1]['file'],role='weapon',reuse='one painted region reused for source-defined mirror instances' if s['count']==2 else False,canonicalSource=evidence[id],adapterAction='draw this independent weapon region with the original Weapon.draw recoil and source-defined mirror/offsets; do not suppress weapon draw')]
 row['assembly']=[dict(file=rel(body['path']),role='body',originPixels=bodyOrigin),dict(file=rel(weapon['path']),role='weapon',scale=s['scale'],instances=mounts,pivotNormalized=[.5,.78],coordinateStatus='estimated_art_alignment; canonical world coordinates retained in officialWeaponOffsets')]
 row['officialWeaponProperties']=evidence[id]['effective']
 row['visualReview']=dict(status='pending',bodyUnderpaint='no weapon texture or transparent hole beneath mounts',weaponIndependent=True,sourceDefinedWeaponInstances=s['count'],engineRuntimeVerified=False)
 patch.append(row)
 # Neutral light and dark contact image contains no new painted artwork.
 pair=Image.new('RGB',(size[0]*2,size[1]),'#eae8df')
 for idx,im in enumerate((rest,recoiled)):
  bg=Image.new('RGBA',size,'#eae8df' if idx==0 else '#203b3d');bg.alpha_composite(im);pair.paste(bg.convert('RGB'),(idx*size[0],0))
 pair.thumbnail((1500,750));q=HERE/(id+'-rest-and-recoil.jpg');pair.save(q,quality=94);diagnostics.append(rel(q))

write(HERE/'patch-manifest.json',dict(schemaVersion=1,worker='coordinator-recoil-fix',status='pending_final_visual_review',createdAt=now(),scope=ids,sourceEvidence='records/coordinator-recoil-fix/source-evidence.json',sourceAtlas=rel(src),assets=patch,diagnostics=diagnostics,actualModel=None,actualQuality=None,runtimeIntegrationVerified=False,mergeInstruction='Replace only these three existing air-erekir assets; do not append duplicate unit IDs. Original moving weapon regions must map to independent weapon PNGs.'))
print(json.dumps({'parts':[{ 'id':i,'role':role,'size':list(a['image'].size),'sourceBox':a['record']['operation']['sourceCropBox']} for (i,role),a in assets.items()],'patchAssets':ids},ensure_ascii=False,indent=2))
