import sys,json,hashlib,datetime
from pathlib import Path
import numpy as np
from PIL import Image
root=Path(r'D:\work\image\mindustry-image');sys.path.insert(0,str(root/'records'))
from pixel_tools import components
out=root/'units/special'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
boards={}; produced=[]; units={}
for p in sorted((out/'boards').glob('*.png')):
    im=Image.open(p).convert('RGBA');arr=np.array(im)
    cs=components(arr[:,:,3]>=16,20)
    boards[p.stem]={'path':p,'im':im,'arr':arr,'cs':cs}
    rp=p.with_name(p.name+'.generation.json');rec=json.loads(rp.read_text(encoding='utf-8'))
    receipt=json.loads((root/'records/workers/special'/f'{p.stem}.tool-receipt.json').read_text(encoding='utf-8'))
    prompt=root/rec['prompt'];prompt.write_text(receipt['submittedArguments']['prompt'],encoding='utf-8');rec['promptSha256']=sha(prompt)
    if len(rec['references'])==3:
        rec['references'][2]['purpose']='scathe_family_shape_reference'
    rec['status']='generated_parts_board_visual_reviewed';rp.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def source_for(board):
    p=boards[board]['path']
    return {'file':p.relative_to(root).as_posix(),'sha256':sha(p),'generationRecord':p.with_name(p.name+'.generation.json').relative_to(root).as_posix()}

def extract(board,c):
    b=boards[board];a=b['arr'];mask=np.zeros(a.shape[:2],dtype=bool)
    for y,s,e in c['runs']: mask[y,s:e]=True
    clean=np.zeros_like(a);clean[mask]=a[mask]
    x0,y0,x1,y1=c['bbox']
    return Image.fromarray(clean[y0:y1,x0:x1],'RGBA')

def save(im, rel, sources, operation, extra=None):
    p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
    rec={'schemaVersion':1,'file':rel,'pathBase':'mindustry-image/','createdAt':now(),'kind':'derived_image','tool':'local Pillow / NumPy','route':'local_authorized_pixel_processing','format':'PNG','mode':'RGBA','width':im.width,'height':im.height,'sha256':sha(p),'derivedFrom':sources,'operation':operation,'resized':False,'actualModel':None,'actualQuality':None,'modelEvidence':'继承来源记录；本地处理未调用生成模型。','alphaExtrema':im.getchannel('A').getextrema()}
    if extra:rec.update(extra)
    p.with_name(p.name+'.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    produced.append(rec);return rec

def padded(im,pad=32):
    canvas=Image.new('RGBA',(im.width+2*pad,im.height+2*pad));canvas.alpha_composite(im,(pad,pad));return canvas

def ordinary(board,c,uid):
    im=extract(board,c);canvas=padded(im)
    rec=save(canvas,f'units/special/assets/{uid}.png',[source_for(board)],{'type':'connected_component_extract_crop_pad','sourceBBox':c['bbox'],'mask':'alpha >= 16; isolated components below area 20 excluded','padding':32,'pixelResampling':False,'hiddenRGB':'zeroed outside retained alpha mask'})
    units[uid]={'id':uid,'file':rec['file'],'layers':[{'role':'body','file':rec['file'],'pivot':'canvas_center','forward':'up'}],'nativeExtractedSize':[im.width,im.height],'outputSize':[canvas.width,canvas.height],'sourceBoards':[board],'operation':'native component extraction, 32px transparent padding; no resize','effects':'使用官方程序引擎／尾迹／爆炸效果，不烘焙在主体PNG。','runtimeVerified':False}
    return rec

b='01-drones-target-v1'
for uid,c in zip(['manifold','assembly-drone','dummy'],sorted(boards[b]['cs'],key=lambda c:c['bbox'][0])):
    ordinary(b,c,uid)

b='04-scathe-variants-v1'
for uid,c in zip(['scathe-missile-phase','scathe-missile-surge','scathe-missile-surge-split'],sorted(boards[b]['cs'],key=lambda c:c['bbox'][0])):
    ordinary(b,c,uid)

b='03-main-missiles-v1';cs=boards[b]['cs']
top=sorted([c for c in cs if c['bbox'][1]<500],key=lambda c:c['bbox'][0])
ordinary(b,top[0],'anthicus-missile');ordinary(b,top[1],'quell-missile')
ordinary(b,next(c for c in cs if c['bbox'][0]>700 and c['bbox'][1]>500),'scathe-missile')
parts=sorted([c for c in cs if c['bbox'][0]<700 and c['bbox'][1]>500],key=lambda c:c['bbox'][0])
placements=[]
for label,c,shift in zip(['left-fin','body','right-fin'],parts,[(80,-45),(0,0),(-80,-45)]):
    placements.append((label,c,extract(b,c),c['bbox'][0]+shift[0],c['bbox'][1]+shift[1]))
x0=min(p[3] for p in placements);y0=min(p[4] for p in placements);x1=max(p[3]+p[2].width for p in placements);y1=max(p[4]+p[2].height for p in placements)
size=(x1-x0+64,y1-y0+64);layers=[];combined=Image.new('RGBA',size)
for label,c,im,x,y in placements:
    pos=(x-x0+32,y-y0+32);can=Image.new('RGBA',size);can.alpha_composite(im,pos)
    rec=save(can,f'units/special/layers/disrupt-missile-{label}.png',[source_for(b)],{'type':'component_crop_and_translate_to_common_canvas','sourceBBox':c['bbox'],'destination':list(pos),'mask':'alpha >= 16','pixelResampling':False}, {'pivotNote':'body uses canvas center; fin hinge estimates in unit manifest require runtime verification'})
    layers.append({'role':label,'file':rec['file'],'pivot':([231-x0+32,1013-y0+32] if label=='left-fin' else [435-x0+32,1013-y0+32] if label=='right-fin' else [size[0]/2,size[1]/2]),'pivotStatus':'estimated_art_alignment'})
for role in ['left-fin','right-fin','body']:
    p=root/next(l['file'] for l in layers if l['role']==role);combined.alpha_composite(Image.open(p).convert('RGBA'))
src=[{'file':l['file'],'sha256':sha(root/l['file']),'generationRecord':l['file']+'.generation.json'} for l in layers]
rec=save(combined,'units/special/assets/disrupt-missile.png',src,{'type':'alpha_composite_existing_layers','order':['left-fin','right-fin','body'],'pixelResampling':False})
units['disrupt-missile']={'id':'disrupt-missile','file':rec['file'],'layers':layers,'outputSize':list(size),'sourceBoards':[b],'operation':'native body and separate fins translated to common canvas; assembled preview','effects':'官方紫色抑制效果与尾迹复用；尾翼独立旋转，需按实际RegionPart配置验证。','runtimeVerified':False}

b='02-neoplasm-segments-v1';cs=boards[b]['cs']
for uid,selected in [('renale',[c for c in cs if c['bbox'][0]<600]),('latum',[c for c in cs if c['bbox'][0]>600])]:
    selected.sort(key=lambda c:c['bbox'][1]);images=[extract(b,c) for c in selected]
    overlap=32;w=max(im.width for im in images)+64;h=sum(im.height for im in images)-overlap*(len(images)-1)+64
    canvas=Image.new('RGBA',(w,h));layers=[];y=32
    for i,(c,im) in enumerate(zip(selected,images)):
        seg=len(images)-1-i
        pos=((w-im.width)//2,y);layer=Image.new('RGBA',(w,h));layer.alpha_composite(im,pos)
        rec=save(layer,f'units/special/layers/{uid}-segment{seg}.png',[source_for(b)],{'type':'segment_component_crop_translate','sourceBBox':c['bbox'],'destination':list(pos),'commonCanvas':[w,h],'mask':'alpha >= 16','pixelResampling':False,'plannedOverlapPx':overlap})
        layers.append({'segmentIndex':seg,'role':('head' if i==0 else 'tail' if i==len(images)-1 else 'torso'),'file':rec['file'],'pivot':[w/2,h/2],'sourceBBox':c['bbox'],'destination':list(pos)})
        y+=im.height-overlap
    # Match UnitType.drawCrawl: segment0 tail drawn first, head last.
    for l in sorted(layers,key=lambda l:l['segmentIndex']):
        canvas.alpha_composite(Image.open(root/l['file']).convert('RGBA'))
    src=[{'file':l['file'],'sha256':sha(root/l['file']),'generationRecord':l['file']+'.generation.json'} for l in layers]
    rec=save(canvas,f'units/special/assets/{uid}.png',src,{'type':'alpha_composite_native_segment_layers','drawOrder':'segment0..N (tail to head)','pixelResampling':False,'overlapPx':overlap})
    units[uid]={'id':uid,'file':rec['file'],'layers':sorted(layers,key=lambda l:l['segmentIndex']),'segments':len(images),'outputSize':[w,h],'sourceBoards':[b],'operation':'native independent segments assembled; no new generated detail or resize','effects':'官方蠕动、回血与neoplasm液体效果复用；分段共享中心旋转，摆动幅度需运行验收。','runtimeVerified':False}
(root/'records/workers/special/extraction.json').write_text(json.dumps({'schemaVersion':1,'generatedAt':now(),'assets':list(units.values()),'derivedPngCount':len(produced),'processing':'Explicitly authorized local pixel cleanup, connected-component extraction, translation and alpha compositing only.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for uid,u in units.items():
    im=Image.open(root/u['file']).convert('RGBA')
    for label,color in [('dark',(28,36,39,255)),('light',(240,236,224,255))]:
        bg=Image.new('RGBA',im.size,color);bg.alpha_composite(im)
        save(bg,f'records/workers/special/qa/{uid}-{label}.png',[{'file':u['file'],'sha256':sha(root/u['file']),'generationRecord':u['file']+'.generation.json'}],{'type':'alpha_composite_inspection_backdrop','background':color,'inspectionOnly':True,'pixelResampling':False})
print(json.dumps({'units':len(units),'derivedUnitAndLayerPngs':len(produced)-24,'ids':list(units),'sizes':{uid:u['outputSize'] for uid,u in units.items()}},ensure_ascii=False))
