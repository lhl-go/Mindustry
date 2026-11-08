import json,hashlib,sys
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
sys.path.insert(0,str(ROOT/'records'))
from pixel_tools import components
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(im,out,source,operation,key):
    out.parent.mkdir(parents=True,exist_ok=True);im.save(out)
    r={'schemaVersion':1,'semanticKey':key,'file':out.relative_to(ROOT).as_posix(),'sha256':sha(out),'width':im.width,'height':im.height,'derivedAt':datetime.now(timezone.utc).isoformat(),'derivedFrom':{'file':source.relative_to(ROOT).as_posix(),'sha256':sha(source),'generationRecord':source.relative_to(ROOT).as_posix()+'.generation.json'},'operation':operation,'actualModel':None,'actualQuality':None,'validation':{'alphaExtrema':list(im.getchannel('A').getextrema()),'visualReview':'pending','runtime':'unverified'}}
    out.with_suffix('.png.derived.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return r
def clean_cells(source,cols,rows):
    a=np.array(Image.open(source).convert('RGBA'));h,w=a.shape[:2];alpha=a[:,:,3]
    groups=components(alpha>=16,min_area=28);cells=[[]for _ in range(cols*rows)]
    for g in groups:
        x0,y0,x1,y1=g['bbox'];idx=min(rows-1,int((y0+y1)/2*rows/h))*cols+min(cols-1,int((x0+x1)/2*cols/w));cells[idx].append(g)
    result=[]
    for cell in cells:
        mask=np.zeros((h,w),dtype=bool)
        for g in cell:
            for y,x0,x1 in g['runs']:mask[y,x0:x1]=True
        assert mask.sum()>500
        p=a.copy();p[:,:,3]=np.clip(np.rint((alpha.astype(float)-8)*255/237),0,255).astype(np.uint8);p[~mask]=0
        im=Image.fromarray(p);box=im.getbbox();cut=im.crop(box);side=max(cut.size)+24;out=Image.new('RGBA',(side,side));out.alpha_composite(cut,((side-cut.width)//2,(side-cut.height)//2))
        result.append((out,box))
    return result
sectors=[]
for batch in json.loads((HERE/'sector-batches.json').read_text()):
    n=batch['batch'];source=HERE/'source'/f'{n+6:02d}-sectors-{n:02d}.png';cols=rows=2 if n==6 else 3
    for i,(im,box) in enumerate(clean_cells(source,cols,rows)):
        name=Path(batch['cells'][i]['sourcePath']).stem
        sectors.append(save(im,HERE/'sectors'/f'{name}.png',source,{'kind':'authorized_alpha_component_crop_padding','grid':[cols,rows],'index':i,'sourceBox':list(box),'alphaCutoff':16,'minComponentArea':28,'alphaRemap':'clip(round((alpha-8)*255/237),0,255)','retainedRGBUnchanged':True,'resampling':False,'padding':12},name))
(HERE/'sectors-manifest.json').write_text(json.dumps({'status':'exported_pending_review','count':len(sectors),'assets':sectors},indent=2)+'\n')
source=HERE/'source/06-title-logo.png'
im,box=clean_cells(source,1,1)[0]
# Keep the title wide; remove square packing after preserving every component.
im=im.crop(im.getbbox());wide=Image.new('RGBA',(im.width+24,im.height+24));wide.alpha_composite(im,(12,12))
save(wide,HERE/'brand/title-logo.png',source,{'kind':'authorized_alpha_component_crop_padding','sourceBox':list(box),'alphaCutoff':16,'resampling':False,'padding':12},'title-logo')
def contact(items,path,background,cols=7,cell=180):
    canvas=Image.new('RGB',(cols*cell,((len(items)+cols-1)//cols)*cell),background);d=ImageDraw.Draw(canvas)
    for i,r in enumerate(items):
        im=Image.open(ROOT/r['file']).convert('RGBA');im.thumbnail((cell-16,cell-48),Image.Resampling.LANCZOS)
        x=i%cols*cell;y=i//cols*cell;canvas.paste(im,(x+(cell-im.width)//2,y+4),im)
        d.text((x+4,y+cell-38),r.get('semanticKey',Path(r['file']).stem).replace('sector-',''),fill='#e8dcc3'if background=='#172b2c'else'#173b35')
        sm=Image.open(ROOT/r['file']).convert('RGBA');sm.thumbnail((32,32),Image.Resampling.LANCZOS);canvas.paste(sm,(x+cell-36,y+cell-36),sm)
    canvas.save(path,quality=94)
contact(sectors,HERE/'qa/sectors-light.jpg','#eee8d9')
contact(sectors,HERE/'qa/sectors-dark.jpg','#172b2c')
icons=json.loads((HERE/'icons-manifest.json').read_text())['assets']
contact(icons,HERE/'qa/icons-dark-small.jpg','#172b2c',8,150)
refs=[]
for a in json.loads((HERE/'source-inventory.json').read_text())['assets']:
    p=a['sourcePath']
    if '/sprites/ui/'in p and '/sectors/'not in p or '/blocks/extra/'in p or p.endswith('schematic-background.png'):
        refs.append({'file':a['localReference'],'semanticKey':Path(p).name})
contact(refs,HERE/'qa/original-ui-controls.jpg','#eee8d9',8,150)
print(json.dumps({'sectors':len(sectors),'icons':len(icons),'contactSheets':4}))
