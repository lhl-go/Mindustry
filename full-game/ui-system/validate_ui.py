import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(HERE/'manifest.json');inventory={x['sourcePath']:x for x in read(HERE/'source-inventory.json')['assets']};errors=[];nine=0
for a in m['assets']:
    p=ROOT/a['file'];ref=ROOT/inventory[a['sourcePath']]['localReference']
    if sha(p)!=a['sha256']:errors.append('hash:'+a['sourcePath'])
    for source in a['derivedFrom']:
        q=ROOT/source['file']
        if not q.exists()or sha(q)!=source['sha256']:errors.append('source:'+a['sourcePath'])
    if p.name.endswith('.9.png'):
        nine+=1;old=np.array(Image.open(ref).convert('RGBA'));new=np.array(Image.open(p).convert('RGBA'))
        for v,w in [(old[0],new[0]),(old[-1],new[-1]),(old[:,0],new[:,0]),(old[:,-1],new[:,-1])]:
            if not np.array_equal(v,w):errors.append('nine_patch_metadata:'+a['sourcePath'])
    if p.suffix=='.png':
        im=Image.open(p);im.verify();im=Image.open(p)
        if list(im.size)!=a['sourceSize']:errors.append('size:'+a['sourcePath'])
    if a['operation']['kind'].startswith('byte_exact')and p.read_bytes()!=ref.read_bytes():errors.append('reuse:'+a['sourcePath'])
if len({x['sourcePath']for x in m['assets']})!=277 or m['unmapped']:errors.append('coverage')
def render9(path,size):
    im=Image.open(path).convert('RGBA');a=np.array(im)
    xs=np.flatnonzero((a[0,:,3]>127)&(a[0,:,:3].sum(axis=1)<32));ys=np.flatnonzero((a[:,0,3]>127)&(a[:,0,:3].sum(axis=1)<32))
    w,h=im.size
    sx=[1,int(xs.min()),int(xs.max())+1,w-1];sy=[1,int(ys.min()),int(ys.max())+1,h-1]
    dx=[0,sx[1]-1,size[0]-(w-1-sx[2]),size[0]];dy=[0,sy[1]-1,size[1]-(h-1-sy[2]),size[1]]
    out=Image.new('RGBA',size)
    for y in range(3):
        for x in range(3):
            if sx[x+1]>sx[x]and sy[y+1]>sy[y]and dx[x+1]>dx[x]and dy[y+1]>dy[y]:
                r=im.crop((sx[x],sy[y],sx[x+1],sy[y+1])).resize((dx[x+1]-dx[x],dy[y+1]-dy[y]),Image.Resampling.LANCZOS);out.paste(r,(dx[x],dy[y]))
    return out
canvas=Image.new('RGB',(1200,850),'#17302d');d=ImageDraw.Draw(canvas)
names=['button.9.png','button-over.9.png','button-down.9.png','button-disabled.9.png','button-red.9.png','pane.9.png','pane-solid.9.png','inventory.9.png','underline-red.9.png','slider-back.9.png','scroll.9.png','button-side-left.9.png']
for i,name in enumerate(names):
    p=HERE/'compat/core/assets-raw/sprites/ui'/name;im=render9(p,(340,140));x=i%3*400+30;y=i//3*210+15;canvas.paste(im,(x,y),im);d.text((x,y+150),name,fill='#eadfc6')
canvas.save(HERE/'qa/ninepatch-expanded.jpg',quality=96)
report={'checkedAt':datetime.now(timezone.utc).isoformat(),'sourcePaths':277,'exportedPaths':len(m['assets']),'ninePatchMetadataExact':nine,'errors':errors,'visualReview':'pending_expanded_ninepatch','runtimeIntegration':'unverified','sourceNativeArtAndCompatibilitySizesAreDistinct':True}
(HERE/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
assert not errors
