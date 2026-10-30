from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import numpy as np,json,hashlib,datetime,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'records'))
from pixel_tools import components
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
source=ROOT/'units/root-builders/boards/01-core-builders-parts-v1.png';im=Image.open(source).convert('RGBA');raw=np.array(im)
parts=components(raw[:,:,3]>=16,min_area=50)
bodies=sorted([p for p in parts if p['bbox'][1]<600],key=lambda p:p['bbox'][0]);weapons=sorted([p for p in parts if p['bbox'][1]>600],key=lambda p:p['bbox'][0]);assert len(bodies)==len(weapons)==3
source_info=dict(file=source.relative_to(ROOT).as_posix(),sha256=sha(source),generationRecord=source.relative_to(ROOT).as_posix()+'.generation.json',nativeSize=list(im.size))
def save_layer(part,file,rotate=False):
 box=part['bbox'];a=raw[box[1]:box[3],box[0]:box[2]].copy();keep=np.zeros(a.shape[:2],dtype=bool)
 for y,s,e in part['runs']:keep[y-box[1],s-box[0]:e-box[0]]=True
 a[:,:,3]=np.where(keep,np.clip(np.round((a[:,:,3].astype(float)-8)*255/237),0,255),0).astype('uint8');a[a[:,:,3]==0,:3]=0
 item=Image.fromarray(a)
 if rotate:item=item.transpose(Image.Transpose.ROTATE_180)
 item=ImageOps.expand(item,32,(0,0,0,0));path=ROOT/file;item.save(path)
 record=dict(file=file,sha256=sha(path),width=item.width,height=item.height,mode='RGBA',derivedFrom=source_info,operation=dict(alphaCutoff=16,alphaRemap='clip(round((a-8)*255/237),0,255)',retainedRgb='unchanged',sourceCropBox=box,padding=32,rotationDegrees=180 if rotate else 0,resampled=False),actualModel=None,actualQuality=None,sourceImageRetained=True,authorization='2026-10-26 user explicitly allowed local cleanup and slicing',runtimeIntegrationVerified=False)
 dump(Path(str(path)+'.derived.json'),record);return item,record
layers={};assets=[]
for i,uid in enumerate(['alpha','beta','gamma']):layers[uid]=save_layer(bodies[i],f'units/root-builders/layers/{uid}-body.png')
layers['small-basic-weapon']=save_layer(weapons[0],'units/root-builders/layers/small-basic-weapon.png',True)
layers['small-mount-weapon']=save_layer(weapons[1],'units/root-builders/layers/small-mount-weapon.png',True)
inv={u['id']:u for u in json.loads((ROOT/'records/inventory-units.json').read_text(encoding='utf-8-sig'))['units']}
for uid,hitsize,mount_x,mount_y in [('alpha',8,2.75,1),('beta',9,3,1),('gamma',11,1,2)]:
 body,bodyrec=layers[uid];weapon_id='small-basic-weapon' if uid=='alpha' else 'small-mount-weapon';weapon,wrec=layers[weapon_id]
 # Art-only placement estimate; actual game draw scale and offsets remain explicit runtime checks.
 px_per_world=(body.width-64)/(hitsize*1.65);weapon_width=round(px_per_world*(2.0 if uid=='alpha' else 2.3))
 wvis=weapon.crop(weapon.getbbox());wvis=wvis.resize((weapon_width,round(wvis.height*weapon_width/wvis.width)),Image.Resampling.LANCZOS)
 composite=Image.new('RGBA',body.size,(0,0,0,0));placements=[]
 for sign in [-1,1]:
  cx=body.width/2+sign*mount_x*px_per_world;cy=body.height/2-mount_y*px_per_world
  at=[round(cx-wvis.width/2),round(cy-wvis.height/2)];composite.alpha_composite(wvis,tuple(at));placements.append(dict(mirrorSide=sign,topLeftPixels=at,size=list(wvis.size),officialOffset=[sign*mount_x,mount_y]))
 composite.alpha_composite(body)
 file=f'units/root-builders/assets/{uid}.png';p=ROOT/file;composite.save(p)
 rec=dict(file=file,sha256=sha(p),width=composite.width,height=composite.height,mode='RGBA',derivedFrom=[dict(file=r['file'],sha256=r['sha256'],generationRecord=r['file']+'.derived.json') for r in [bodyrec,wrec]],operation=dict(kind='static_layer_composite_preview',order=['mirrored_weapon_pair','body'],weaponResampled=True,bodyResampled=False,weaponPlacements=placements,pixelsPerWorldUnitEstimate=px_per_world),actualModel=None,actualQuality=None,runtimeIntegrationVerified=False)
 dump(Path(str(p)+'.derived.json'),rec)
 assets.append(dict(id=uid,officialNameZhCN=inv[uid]['officialNameZhCN'],family=inv[uid]['family'],file=file,generationRecord=file+'.derived.json',sha256=sha(p),size=list(composite.size),status='static_art_exported_runtime_unverified',layers=[dict(role='weapon_mirrored_pair',file=wrec['file'],officialRegion=weapon_id,top=False,mirror=True,officialOffset=[mount_x,mount_y],orientationCorrectionDegrees=180),dict(role='body',file=bodyrec['file'],officialRegion=uid,pivot='canvas_center')],layerFiles=[wrec['file'],bodyrec['file']],layerAlignment=dict(type='estimated_art_alignment',placements=placements,pixelsPerWorldUnit=px_per_world),effects='Reuse official engine plume, build beam, mining beam and laser effects; not baked in PNG.',runtimeVerified=False,sourceBoards=[source_info['file']]))
qa=Image.new('RGB',(1200,900),'#eee8d7');draw=ImageDraw.Draw(qa)
for i,a in enumerate(assets):
 pic=Image.open(ROOT/a['file']);pic.thumbnail((365,385))
 for j,color in enumerate(['#eee8d7','#20312f']):
  x=i*400;y=j*450;qa.paste(color,(x,y,x+400,y+450));qa.paste(pic,(x+(400-pic.width)//2,y+35),pic);draw.text((x+16,y+12),a['id']+' / '+('light' if j==0 else 'dark'),fill='#213e32' if j==0 else '#eadcba')
qa.save(ROOT/'records/workers/root-builders/final-alpha-contact.jpg',quality=95)
verification=[]
for f in sorted(set([a['file'] for a in assets]+[r[1]['file'] for r in layers.values()])):
 image=Image.open(ROOT/f);arr=np.array(image);bbox=image.getbbox();pad=min(bbox[0],bbox[1],image.width-bbox[2],image.height-bbox[3]);verification.append(dict(file=f,sha256=sha(ROOT/f),size=list(image.size),mode=image.mode,alphaExtrema=list(image.getchannel('A').getextrema()),transparentBorder=pad,hiddenRgbZero=bool((arr[arr[:,:,3]==0,:3]==0).all()),passed=pad>=32))
dump(ROOT/'records/workers/root-builders/verification.json',dict(images=verification,visualReview='pending_root_contact_review',runtimeVerified=False))
dump(ROOT/'records/workers/root-builders/manifest.json',dict(schemaVersion=1,worker='root-builders',updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='art_exported_visual_review_pending',assets=assets,board=source_info,uniqueLayerCount=5,independentUnitPngCount=3,actualModel=None,actualQuality=None,notes=['Weapon images were rotated 180 degrees so muzzle points up.','Beta and Gamma share exactly the same small-mount-weapon file, matching the official region reuse.','Composite previews downsample weapon art; native independent body and weapon PNGs are preserved.','A third weapon candidate in the generated board is unused; no false unique-region claim.'],runtimeIntegrationVerified=False))
print('Exported 3 unit composites + 5 native layers')
