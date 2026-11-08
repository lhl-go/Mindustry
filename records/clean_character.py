"""User-authorized alpha cleanup; preserves all retained RGB pixels, no resampling."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
src=ROOT/'characters/02-alchemy-engineer-v1.png'
out=ROOT/'characters/02-alchemy-engineer-clean.png'
rgba=np.array(Image.open(src).convert('RGBA'))
alpha=rgba[:,:,3]
mask=alpha>=16
# Connected components via row runs, with 8-neighbour connectivity.
parent=[]; weights=[]; runs=[]; previous=[]
def find(a):
    while parent[a]!=a:
        parent[a]=parent[parent[a]];a=parent[a]
    return a
def union(a,b):
    a,b=find(a),find(b)
    if a!=b: parent[b]=a
for y,row in enumerate(mask):
    edges=np.diff(np.r_[False,row,False].astype(np.int8))
    starts=np.where(edges==1)[0];ends=np.where(edges==-1)[0]
    current=[]
    for start,end in zip(starts,ends):
        n=len(parent);parent.append(n);weights.append(int(end-start))
        for ps,pe,pn in previous:
            if pe>=start and ps<=end:union(n,pn)
        current.append((int(start),int(end),n));runs.append((y,int(start),int(end),n))
    previous=current
totals={}
for n,w in enumerate(weights):totals[find(n)]=totals.get(find(n),0)+w
largest=max(totals,key=totals.get)
keep=np.zeros(mask.shape,dtype=bool)
for y,start,end,n in runs:
    if find(n)==largest:keep[y,start:end]=True
clean=rgba.copy()
newalpha=np.clip(np.rint((alpha.astype(float)-8)*255/(245-8)),0,255).astype(np.uint8)
newalpha[~keep]=0
clean[:,:,3]=newalpha
clean[~keep,:3]=0
im=Image.fromarray(clean)
bbox=im.getbbox();cut=im.crop(bbox)
padding=48;side=max(cut.size)+padding*2
canvas=Image.new('RGBA',(side,side),(0,0,0,0));offset=((side-cut.width)//2,(side-cut.height)//2)
canvas.alpha_composite(cut,offset);canvas.save(out)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
record=dict(schemaVersion=1,file=out.relative_to(ROOT).as_posix(),sha256=sha(out),
    derivedAt=datetime.now(ZoneInfo('America/New_York')).isoformat(),
    derivedFrom=dict(file=src.relative_to(ROOT).as_posix(),sha256=sha(src),generationRecord='characters/02-alchemy-engineer-v1.png.generation.json',nativeSize=[1254,1254]),
    operation=dict(kind='authorized_alpha_cleanup_crop_and_pad',alphaCutoff=16,componentPolicy='largest_8_connected_component',alphaRemap='clip(round((alpha-8)*255/237),0,255); values>=245 become255',
        rgbPolicy='retained RGB unchanged; removed transparent pixels set RGB zero',sourceCropBox=bbox,padding=padding,canvasOffset=offset,resampling=False,redrawing=False),
    width=side,height=side,format='PNG',mode='RGBA',actualModel=None,actualQuality=None,
    modelEvidence='Derived from source record; not a new model generation.',
    authorization='2026-10-26 user explicitly answered 允许本地清理和切片（推荐）',
    removedComponentCount=len(totals)-1,retainedPixelCount=int(keep.sum()),
    validation=dict(realAlpha=True,visualReview='pending',runtimeIntegration='not_verified'))
(out.with_name(out.name+'.derived.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# A diagnostic composition is only for visual QA, not game artwork.
preview=Image.new('RGB',(side*3,side))
for idx,color in enumerate(['#f1eee4','#23393b','#8c9893']):
    bg=Image.new('RGBA',canvas.size,color);bg.alpha_composite(canvas);preview.paste(bg.convert('RGB'),(idx*side,0))
preview.thumbnail((2100,700));preview.save(ROOT/'records/character-alpha-qa.jpg',quality=94)
print(json.dumps(record,ensure_ascii=True,indent=2))
