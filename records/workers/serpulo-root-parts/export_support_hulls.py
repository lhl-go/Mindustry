from pathlib import Path
import sys,json,hashlib,datetime
from PIL import Image,ImageDraw,ImageFont
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'records'))
from pixel_tools import components
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=ROOT/'units/serpulo-root-parts/14-support-hulls-v2.png'
im=Image.open(source).convert('RGBA');a=np.array(im)
regions=components(a[:,:,3]>=16,1000)
assert len(regions)==5
regions=sorted(regions,key=lambda g:(0 if g['bbox'][1]<100 else 1,g['bbox'][0]))
items=[]
for uid,g in zip(['retusa','oxynoe','cyerce','aegires','navanax'],regions):
 mask=np.zeros(a.shape[:2],dtype=bool)
 for y,s,e in g['runs']:mask[y,s:e]=True
 b=a.copy();b[:,:,3]=np.where(mask,np.clip((a[:,:,3].astype(float)-8)*255/237,0,255),0).astype('uint8');b[b[:,:,3]==0,:3]=0
 crop=Image.fromarray(b).crop(g['bbox']);out=Image.new('RGBA',(crop.width+64,crop.height+64));out.alpha_composite(crop,(32,32))
 file=f'units/serpulo-root-parts/layers/{uid}-body.png';p=ROOT/file;p.parent.mkdir(parents=True,exist_ok=True);out.save(p)
 rec=dict(schemaVersion=1,file=file,sha256=sha(p),createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),derivedFrom=[dict(file=source.relative_to(ROOT).as_posix(),sha256=sha(source),generationRecord=source.relative_to(ROOT).as_posix()+'.generation.json')],operation='Native-resolution connected-component extraction, alpha >=16 isolated-region mask, alpha rescale clip((a-8)*255/237), RGB unchanged except alpha0 pixels zeroed; bbox crop and 32px transparent padding. No resize or repaint.',sourceBox=g['bbox'],nativeSourceSize=list(im.size),exportSize=list(out.size),resized=False,actualModel=None,actualQuality=None,modelEvidence='See source generation record; host did not disclose model or quality.',userAuthorization='2026-10-26 explicit approval for local cleaning and slicing',role='body-only hull',runtimeRegistrationVerified=False)
 (ROOT/(file+'.derived.json')).write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 items.append(dict(id=uid,file=file,sha256=sha(p),generationRecord=file+'.derived.json',role='body',size=list(out.size),sourceBox=g['bbox'],status='art_layer_complete_runtime_pending'))
contact=Image.new('RGB',(1500,900),'#e8e1cf');d=ImageDraw.Draw(contact)
for row,bg in enumerate(['#e8e1cf','#142b29']):
 d.rectangle((0,row*450,1500,(row+1)*450),fill=bg)
 for col,item in enumerate(items):
  pic=Image.open(ROOT/item['file']);pic.thumbnail((280,390),Image.Resampling.LANCZOS);contact.paste(pic,(col*300+(300-pic.width)//2,row*450+35+(390-pic.height)//2),pic)
  d.text((col*300+16,row*450+12),item['id'],fill='black' if row==0 else 'white')
contact.save(ROOT/'records/workers/serpulo-root-parts/final-alpha-contact.jpg',quality=95)
manifest=dict(schemaVersion=1,status='five_support_hull_layers_complete_runtime_pending',sourceGenerationRecord=source.relative_to(ROOT).as_posix()+'.generation.json',assets=items,visualQa='records/workers/serpulo-root-parts/final-alpha-contact.jpg',runtimeIntegrationVerified=False,sourceImageRetained=True)
(ROOT/'records/workers/serpulo-root-parts/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(items,ensure_ascii=False))
