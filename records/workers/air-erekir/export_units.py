from pipeline import *
JOBS=json.loads((HERE/'jobs.json').read_text(encoding='utf-8'))
REGIONS=[
 [[70,35,490,440],[510,0,1024,450],[1030,0,1536,455],[0,450,603,1010],[603,445,1170,1024]],
 [[60,40,430,410],[490,20,935,450],[930,0,1536,465],[0,460,585,975],[580,450,1210,1024]],
 [[90,50,430,455],[560,20,975,460],[1050,0,1515,500],[20,470,495,990],[495,425,1050,1024]],
 [[65,65,450,430],[530,20,1005,470],[1090,0,1510,485],[25,475,545,1000],[540,435,1120,1024]],
 [[110,10,410,465],[545,5,990,465],[1020,0,1536,510],[10,495,530,1024],[525,445,1410,1024]],
 [[65,80,550,605],[640,45,1335,690],[1340,0,2172,724]]
]
def dilate(mask):
    p=np.pad(mask,1)
    return np.logical_or.reduce([p[y:y+mask.shape[0],x:x+mask.shape[1]] for y in range(3) for x in range(3)])
def cut(source,box,target):
    with Image.open(source) as im:arr=np.array(im.convert('RGBA').crop(box))
    labels,parts=connected(arr[:,:,3]>=32)
    if not parts:raise ValueError(str(target))
    keep=dilate(labels==parts[0]['label'])
    arr[:,:,3][~keep]=0
    arr[:,:,3][arr[:,:,3]<16]=0
    arr[:,:,3][arr[:,:,3]>=245]=255
    arr[arr[:,:,3]==0,:3]=0
    im=Image.fromarray(arr)
    b=im.getbbox()
    im=im.crop(b)
    output=Image.new('RGBA',(im.width+32,im.height+32),(0,0,0,0))
    output.alpha_composite(im,(16,16));target.parent.mkdir(parents=True,exist_ok=True);output.save(target)
    return dict(cropRegion=box,trimBoundsInRegion=list(b),padding=16,alphaLowThreshold=16,opaqueThreshold=245,keepLargestConnectedComponent=True,dilatePixels=1,width=output.width,height=output.height)
assets=[]
for j,boxes in zip(JOBS,REGIONS):
 source=ROOT/'units/air-erekir/source'/(j['stem']+'.png')
 for name,box in zip(j['names'],boxes):
    target=ROOT/'units/air-erekir/individual'/(name+'.png')
    operation=cut(source,box,target)
    record=dict(schemaVersion=1,id=name,file=target.relative_to(ROOT).as_posix(),sha256=sha(target),width=operation['width'],height=operation['height'],format='PNG',mode='RGBA',derivedFrom=[dict(file=source.relative_to(ROOT).as_posix(),sha256=sha(source),generationRecord=source.relative_to(ROOT).as_posix()+'.generation.json')],operation=dict(type='native_pixel_crop_and_alpha_cleanup',**operation),actualModel=None,actualQuality=None,sourceModelEvidence='See native source generation record; host did not disclose exact model or quality.',upsampled=False,anchorNormalized=[0.5,0.5],facing='north',engineRuntimeVerified=False)
    record_path=target.with_name(target.name+'.generation.json');write(record_path,record)
    assets.append(dict(id=name,file=target.relative_to(ROOT).as_posix(),generationRecord=record_path.relative_to(ROOT).as_posix(),sha256=sha(target),size=[operation['width'],operation['height']],compositePreview=target.relative_to(ROOT).as_posix(),layers=[],layerFiles=[],status='composite_exported_required_layers_in_progress',engineNotVerified=True))
write(HERE/'manifest.json',dict(schemaVersion=1,worker='air-erekir',updatedAt=datetime.now(timezone.utc).isoformat(),status='independent_units_exported_layer_production_in_progress',assets=assets))
# One real-composite QA contact sheet, three backgrounds per selected unit.
thumb=220;gap=16;cols=7;rows=4
sheet=Image.new('RGB',(cols*(thumb+gap)+gap,rows*(thumb+44)+gap),(232,225,204));d=ImageDraw.Draw(sheet)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
for i,a in enumerate(assets):
    im=Image.open(ROOT/a['file']).convert('RGBA');im.thumbnail((thumb,thumb),Image.Resampling.LANCZOS)
    x=gap+(i%cols)*(thumb+gap);y=gap+(i//cols)*(thumb+44)
    bg=(35,42,45) if i%3==0 else ((245,240,222) if i%3==1 else (125,125,125))
    tile=Image.new('RGBA',(thumb,thumb),bg+(255,));tile.alpha_composite(im,((thumb-im.width)//2,(thumb-im.height)//2))
    sheet.paste(tile.convert('RGB'),(x,y));d.text((x,y+thumb+8),a['id'],font=font,fill=(20,55,47))
sheet.save(ROOT/'units/air-erekir/units-contact.png')
write(HERE/'contact-derived.json',dict(file='units/air-erekir/units-contact.png',operation='QA contact sheet from actual exported alpha compositing; downscaled for review only',sources=[a['file'] for a in assets]))
print(json.dumps(dict(unitCount=len(assets),manifest='records/workers/air-erekir/manifest.json'),indent=2))
