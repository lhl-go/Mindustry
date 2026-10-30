import hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image,ImageDraw

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
sys.path.insert(0,str(ROOT/'records'))
from pixel_tools import components

plans={
'01-navigation-tools':(6,4,'about add admin arrow-note book break changelog chat check command-attack command-rally copy crafting defense diagonal distribution donate dots download editor effect elevation eraser exit'.split()),
'02-files-map':(6,4,'eye eye-off file-image file-text file fill flip folder-parent grid hammer home host info item line link liquid-consume liquid load-image load loading lock-open lock map'.split()),
'03-actions-modes':(6,4,'menu missing mode-attack mode-pvp mode-survival none paste pencil pick play-2 players production quit redo rename resize rotate-arrow rotate-left rotate-right rotate save-image spray terrain tools'.split()),
'04-cursors-mascots':(4,4,'trash tree tutorial undo units upload cursor drill hand ibeam repair target unload logic-node cat ranai'.split())}
outdir=HERE/'icons';outdir.mkdir(exist_ok=True)
qadir=HERE/'qa';qadir.mkdir(exist_ok=True)
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assets=[]
for board,(cols,rows,names) in plans.items():
    source=HERE/'source'/f'{board}.png'
    if not source.exists():continue
    rgba=np.array(Image.open(source).convert('RGBA'))
    h,w=rgba.shape[:2];alpha=rgba[:,:,3]
    groups=components(alpha>=16,min_area=28)
    cells=[[] for _ in names]
    for group in groups:
        x0,y0,x1,y1=group['bbox'];cx=(x0+x1)/2;cy=(y0+y1)/2
        col=min(cols-1,int(cx*cols/w));row=min(rows-1,int(cy*rows/h))
        cells[row*cols+col].append(group)
    preview=Image.new('RGB',(cols*240,rows*260),'#eae5d6')
    draw=ImageDraw.Draw(preview)
    for i,name in enumerate(names):
        mask=np.zeros((h,w),dtype=bool)
        for g in cells[i]:
            for y,x0,x1 in g['runs']:mask[y,x0:x1]=True
        assert mask.sum()>200,name
        clean=rgba.copy();a=np.clip(np.rint((alpha.astype(float)-8)*255/237),0,255).astype(np.uint8)
        a[~mask]=0;clean[:,:,3]=a;clean[~mask,:3]=0
        im=Image.fromarray(clean);bbox=im.getbbox();cut=im.crop(bbox)
        side=max(cut.size)+24;canvas=Image.new('RGBA',(side,side));offset=((side-cut.width)//2,(side-cut.height)//2)
        canvas.alpha_composite(cut,offset)
        file=outdir/f'{name}.png';canvas.save(file)
        record={'schemaVersion':1,'semanticKey':name,'file':file.relative_to(ROOT).as_posix(),
            'sha256':hashfile(file),'width':side,'height':side,'nativeCropPixels':list(cut.size),
            'derivedAt':datetime.now(timezone.utc).isoformat(),
            'derivedFrom':{'file':source.relative_to(ROOT).as_posix(),'sha256':hashfile(source),
                'generationRecord':source.relative_to(ROOT).as_posix()+'.generation.json','nativeSize':[w,h]},
            'operation':{'kind':'alpha_component_group_crop_and_padding','grid':[cols,rows],
                'cellIndex':i,'sourceBox':list(bbox),'alphaCutoff':16,'minimumComponentArea':28,
                'componentGrouping':'complete components assigned by bbox midpoint; no component cut on cell lines',
                'alphaRemap':'clip(round((alpha-8)*255/237),0,255)',
                'retainedRGBUnchanged':True,'resampling':False,'padding':12,'canvasOffset':list(offset)},
            'actualModel':None,'actualQuality':None,'modelEvidence':'Inherited from source, not newly generated',
            'validation':{'realAlpha':True,'alphaExtrema':list(canvas.getchannel('A').getextrema()),
                          'visualReview':'pending','runtime':'unverified'}}
        assert record['validation']['alphaExtrema']==[0,255]
        file.with_suffix('.png.derived.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        assets.append(record)
        small=canvas.copy();small.thumbnail((218,218))
        px=i%cols*240+(240-small.width)//2;py=i//cols*260+8+(220-small.height)//2
        preview.paste(small,(px,py),small)
        draw.text((i%cols*240+12,i//cols*260+238),name,fill='#173b35')
    preview.save(qadir/f'{board}-light.jpg',quality=94)
manifest={'schemaVersion':1,'status':'exported_pending_visual_review','count':len(assets),'assets':assets}
(HERE/'icons-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'count':len(assets),'boards':len(plans),'status':manifest['status']}))
