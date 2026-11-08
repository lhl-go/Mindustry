from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import numpy as np,json,hashlib,math,datetime,sys
from inspect_components import components

ROOT=Path(__file__).resolve().parents[3]
REPO=ROOT.parent
OWN=ROOT/'units/serpulo-ground-naval'
REC=ROOT/'records/workers/serpulo-ground-naval'
PROMPT=ROOT/'prompts/serpulo-ground-naval'
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat()
CONFIG=json.loads((REPO/'config/image-generation.json').read_text(encoding='utf-8-sig'))
INVENTORY=json.loads((ROOT/'records/inventory-units.json').read_text(encoding='utf-8-sig'))
UNITS={u['id']:u for u in INVENTORY['units']}
for d in ['bodies','parts','sprites']:(OWN/d).mkdir(exist_ok=True)
def rel(p):return Path(p).relative_to(ROOT).as_posix()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,obj):Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def image_stats(im):
    a=np.array(im);al=a[:,:,3]; b=im.getbbox()
    return dict(width=im.width,height=im.height,format='PNG',mode='RGBA',alphaMin=int(al.min()),alphaMax=int(al.max()),transparentPixelCount=int((al==0).sum()),opaquePixelCount=int((al==255).sum()),partialPixelCount=int(((al>0)&(al<255)).sum()),transparentRgbIsZero=bool(np.all(a[al==0,:3]==0)),contentBounds=list(b) if b else None,clearCanvasBorder=bool(np.all(al[0]==0) and np.all(al[-1]==0) and np.all(al[:,0]==0) and np.all(al[:,-1]==0)))
def clean_array(a):
    a=a.copy();a[a[:,:,3]<16]=0;a[:,:,3][a[:,:,3]>=245]=255
    return a

SOURCES={}
for receipt_path in REC.glob('*.tool-receipt.json'):
    receipt=json.loads(receipt_path.read_text(encoding='utf-8-sig')); stem=receipt['stem'];p=OWN/'boards'/f'{stem}.png'
    if not p.exists():continue
    args=receipt['submittedArguments']; prompt=PROMPT/f'{stem}.txt';prompt.write_text(args['prompt'],encoding='utf-8')
    im=Image.open(p);refs=[]
    for i,x in enumerate(args.get('referenced_image_paths',[])):
        rp=Path(x);refs.append(dict(file=str(rp),sha256=sha(rp),role='edit-target' if i==0 and rp.is_relative_to(OWN) else 'primary-style-reference'))
    g=dict(schemaVersion=1,file=rel(p),sha256=sha(p),generatedAt=receipt['returnedAt'],startedAt=receipt['startedAt'],native=dict(width=im.width,height=im.height,format='PNG',mode=im.mode),tool='image_gen.imagegen',route='builtin',configSnapshot=CONFIG,submittedParameters=dict(model=None,quality=None,transparent_background=args.get('transparent_background')),actualModel=None,actualQuality=None,unverifiedReason='宿主管理，工具未开放型号/质量参数且未披露可核实的型号或质量返回元数据。配置与提示词仅表示目标。',prompt=rel(prompt),promptSha256=sha(prompt),references=refs,evidence=dict(toolReceipt=rel(receipt_path),returnedFields=receipt['returnedFields'],outputHint=receipt['outputHint']),sourceImageRetained=True,disposition='rejected_front_oblique_view' if stem.startswith(('01-','02-')) else ('superseded_by_body_only_edit' if stem.startswith(('04-','05-')) else 'native_production_source'))
    gp=REC/f'{stem}.generation.json';write(gp,g);SOURCES[stem]={'file':rel(p),'sha256':g['sha256'],'generationRecord':rel(gp),'nativeSize':[im.width,im.height]}

PARTS={};BODIES={};CROPS=[]
def extract(stem,names,row_counts,kind,anchors=None):
    src=OWN/'boards'/f'{stem}.png';a=clean_array(np.asarray(Image.open(src).convert('RGBA')))
    cs=[c for c in components(a[:,:,3]>0) if c[4]>1000]
    assert len(cs)==len(names),(stem,len(cs))
    cs.sort(key=lambda c:(c[1]+c[3])/2);ordered=[];offset=0
    for n in row_counts:
        row=cs[offset:offset+n];row.sort(key=lambda c:(c[0]+c[2])/2);ordered+=row;offset+=n
    for i,(name,c) in enumerate(zip(names,ordered)):
        x0,y0,x1,y1,area,runs=c
        pixels=np.zeros((y1-y0,x1-x0,4),np.uint8)
        for rx0,y,rx1 in runs:pixels[y-y0,rx0-x0:rx1-x0]=a[y,rx0:rx1]
        im=Image.fromarray(pixels);pad=16;out=Image.new('RGBA',(im.width+pad*2,im.height+pad*2));out.alpha_composite(im,(pad,pad))
        p=OWN/('bodies' if kind=='body' else 'parts')/f'{name}.png';out.save(p)
        an=(anchors or {}).get(name,[.5,.5]); anchor=[round(pad+an[0]*im.width,3),round(pad+an[1]*im.height,3)]
        operation={'type':'authorized_local_alpha_cleanup_connected_component_crop','alphaBelow16':'clear_alpha_and_RGB','alphaAtLeast245':'set_opaque','componentIsolation':'retain every pixel of this connected subject; discard unrelated components','sourceBounds':[x0,y0,x1,y1],'padding':pad,'resized':False,'upscaled':False}
        rec=dict(schemaVersion=1,file=rel(p),sha256=sha(p),createdAt=NOW,route='local-derived',tool='Python/Pillow',derivedFrom=[SOURCES[stem]],operation=operation,actualModel=None,actualQuality=None,modelEvidence='See source generationRecord; no new model call',image=image_stats(out),anchorPx=anchor,anchorBasis='visually selected center or visible pivot; engine alignment unverified',forward='up / negative image y' if kind=='body' or 'leg' not in name else 'segment proximal joint at top; distal at bottom',role=kind)
        gp=p.with_suffix('.png.generation.json');write(gp,rec)
        meta=dict(file=rel(p),sha256=rec['sha256'],generationRecord=rel(gp),width=out.width,height=out.height,anchorPx=anchor,sourceStem=stem,sourceBounds=[x0,y0,x1,y1])
        (BODIES if kind=='body' else PARTS)[name]=meta;CROPS.append(meta)

extract('07-assault-bodies','dagger mace fortress scepter reign'.split(),[3,2],'body')
extract('08-support-bodies','nova pulsar quasar vela corvus'.split(),[3,2],'body')
extract('03-spider-bodies','crawler atrax spiroct arkyid toxopid'.split(),[3,2],'body')
extract('13-assault-hulls','risso minke bryde sei omura'.split(),[3,2],'body')
mech='autocannon flame-pair mortar heavy-burst siege-shotgun repair-bolt electric-coil beam-laser continuous-laser sap-emitter purple-artillery shock-cannon'.split()
naval='deck-cannon missile-pair deck-mortar long-artillery missile-six railgun repair-lens plasma-flame point-defense plasma-missile emp-cannon plasma-laser'.split()
extract('09-mech-weapons',['mech-'+x for x in mech],[4,4,4],'part',{('mech-'+x):[.5,.77] for x in mech})
extract('11-naval-weapons',['naval-'+x for x in naval],[4,4,4],'part',{('naval-'+x):[.5,.75] for x in naval})
leg_names='leg-light leg-heavy leg-crawler leg-upper leg-lower leg-foot'.split()
extract('10-locomotion-parts',leg_names,[3,3],'part',{x:[.5,.14] for x in leg_names})

external=json.loads((ROOT/'records/workers/serpulo-root-parts/manifest.json').read_text(encoding='utf-8-sig'))
for x in external['assets']:
    p=ROOT/x['file'];im=Image.open(p);BODIES[x['id']]={**x,'file':x['file'],'sha256':sha(p),'width':im.width,'height':im.height,'anchorPx':[im.width/2,im.height/2]}

# Each entry is an actual original Weapon region and authored preview placement.
# Tuple: generated part, official region, normalized body x/y mount, part width/body width, rotates, official source x/y.
W={}
def pair(unit,part,region,x,y,width,rotate=False,source_xy=None):
    for side in [-1,1]:W.setdefault(unit,[]).append((part,region,side*x,y,width,rotate,([side*source_xy[0],source_xy[1]] if source_xy else None)))
def single(unit,part,region,x,y,width,rotate=False,source_xy=None):W.setdefault(unit,[]).append((part,region,x,y,width,rotate,source_xy))
pair('dagger','mech-autocannon','large-weapon',.43,-.02,.31,False,[4,2])
pair('mace','mech-flame-pair','flamethrower',.43,-.02,.31)
pair('fortress','mech-mortar','artillery',.44,.01,.30,False,[9,1])
pair('scepter','mech-heavy-burst','scepter-weapon',.43,0,.32,False,[16,1])
pair('scepter','mech-autocannon','scepter-mount',.18,-.18,.17,True,[8.5,6])
pair('scepter','mech-autocannon','scepter-mount',.18,.25,.17,True,[8.5,-7])
pair('reign','mech-siege-shotgun','reign-weapon',.43,.03,.34,False,[21.5,1])
pair('nova','mech-repair-bolt','heal-weapon',.43,0,.32,False,[4.5,0])
pair('pulsar','mech-electric-coil','heal-shotgun-weapon',.42,.03,.30,False,[5,.5])
pair('quasar','mech-beam-laser','beam-weapon',.43,0,.29,False,[6.5,0])
single('vela','mech-continuous-laser','vela-weapon',0,.12,.30,False,[0,0])
pair('vela','naval-repair-lens','repair-beam-weapon-center-large',.30,.30,.20,True,[11,-7.5])
single('corvus','mech-continuous-laser','corvus-weapon',0,.15,.40,False,[0,0])
pair('atrax','mech-flame-pair','atrax-weapon',.28,.05,.28,False,[7,0])
pair('spiroct','mech-sap-emitter','spiroct-weapon',.30,.15,.25,True,[8.5,-1.5])
pair('spiroct','mech-sap-emitter','mount-purple-weapon',.16,-.15,.20,True,[4,3])
for x,y,w,sx,sy in [(.12,-.22,.16,4,8),(.28,-.12,.18,9,6),(.39,.12,.18,14,0)]:pair('arkyid','mech-sap-emitter','spiroct-weapon',x,y,w,True,[sx,sy])
pair('arkyid','mech-purple-artillery','large-purple-mount',.20,.27,.23,True,[9,-7])
pair('toxopid','mech-purple-artillery','large-purple-mount',.27,.12,.25,True,[11,-5])
single('toxopid','mech-shock-cannon','toxopid-cannon',0,.35,.30,True,[0,-14])
pair('risso','naval-deck-cannon','mount-weapon',.23,-.08,.33,True,[4,1.5]);single('risso','naval-missile-pair','missiles-mount',0,.23,.38,True,[0,-5])
pair('minke','naval-deck-cannon','mount-weapon',.24,-.12,.25,True,[5,3.5]);pair('minke','naval-deck-mortar','artillery-mount',.22,.23,.27,True,[5,-5])
single('bryde','naval-long-artillery','large-artillery',0,.13,.40,True,[0,-3.5]);pair('bryde','naval-missile-pair','missiles-mount',.34,.19,.24,True,[8.5,-9])
single('sei','naval-missile-six','sei-launcher',0,0,.40,True,[0,0]);pair('sei','naval-deck-cannon','large-bullet-mount',.28,.30,.28,True,[17.5,-16.5])
single('omura','naval-railgun','omura-cannon',0,-.06,.39,True,[0,-3.5])
single('retusa','naval-repair-lens','repair-beam-weapon-center',0,.28,.30,True,[0,-5.5]);pair('retusa','naval-deck-cannon','retusa-weapon',.28,.10,.25,True,[4.5,-3.5])
pair('oxynoe','naval-plasma-flame','plasma-mount-weapon',.25,-.15,.27,True,[4.5,6.5]);single('oxynoe','naval-point-defense','point-defense-mount',0,.10,.25,True,[0,1])
pair('cyerce','naval-repair-lens','repair-beam-weapon-center',.29,.29,.23,True,[11,-10]);pair('cyerce','naval-plasma-missile','plasma-missile-mount',.27,-.05,.28,True,[9,3])
for sy,y in [(-18,.30),(14,-.18)]:pair('aegires','naval-point-defense','point-defense-mount',.30,y,.18,True,[12.5,sy])
pair('navanax','naval-emp-cannon','emp-cannon-mount',.22,.10,.30,True,[17.5,-6.5])
for sy,y in [(-29.25,.34),(12.5,-.17)]:pair('navanax','naval-plasma-laser','plasma-laser-mount',.38,y,.20,True,[21,sy])

ASSETS=[]
def load(meta):return Image.open(ROOT/meta['file']).convert('RGBA')
def place(canvas,meta,dest,scale,angle=0,anchor=None,mirror=False):
    im=load(meta); ax,ay=anchor or meta['anchorPx']; scale=min(1,scale)
    size=(max(1,round(im.width*scale)),max(1,round(im.height*scale)));sx=size[0]/im.width;sy=size[1]/im.height
    ax*=sx;ay*=sy;im=im.resize(size,Image.Resampling.LANCZOS)
    if mirror:im=ImageOps.mirror(im);ax=im.width-ax
    cx,cy=im.width/2,im.height/2;t=math.radians(angle)
    out=im.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
    ox=(ax-cx)*math.cos(t)+(ay-cy)*math.sin(t)+out.width/2
    oy=-(ax-cx)*math.sin(t)+(ay-cy)*math.cos(t)+out.height/2
    xy=(round(dest[0]-ox),round(dest[1]-oy));canvas.alpha_composite(out,xy)
    return dict(file=meta['file'],generationRecord=meta['generationRecord'],sourceAnchorPx=anchor or meta['anchorPx'],targetAnchorPx=[round(dest[0],3),round(dest[1],3)],scale=[sx,sy],rotationDegreesCCW=angle,mirrorHorizontal=mirror,topLeft=xy,upscaled=False)

ids='dagger mace fortress scepter reign nova pulsar quasar vela corvus crawler atrax spiroct arkyid toxopid risso minke bryde sei omura retusa oxynoe cyerce aegires navanax'.split()
for id in ids:
    body=BODIES[id];u=UNITS[id];bw,bh=body['width'],body['height'];canvas=Image.new('RGBA',(2200,2200));center=(1100,1100);layers=[];placements=[]
    def add(part,role,dest,scale,angle=0,anchor=None,mirror=False,**extra):
        meta=PARTS[part] if isinstance(part,str) else part
        tr=place(canvas,meta,dest,scale,angle,anchor,mirror);placements.append(tr)
        layers.append(dict(file=meta['file'],role=role,sha256=meta['sha256'],generationRecord=meta['generationRecord'],anchorPx=meta['anchorPx'],placement=tr,**extra));return tr
    legs= {'corvus':4,'atrax':4,'spiroct':6,'arkyid':6,'toxopid':8}.get(id,0)
    if u['mobility']=='biped_mech':
        p='leg-crawler' if id=='crawler' else ('leg-heavy' if id in ['scepter','reign','vela'] else 'leg-light')
        for side in [-1,1]:
            meta=PARTS[p];scale=min(1,bh*.67/meta['height'])
            add(p,'locomotion_leg',(center[0]+side*bw*.29,center[1]+bh*.05),scale,side*18,mirror=(side<0),engineRegion=f'{id}-leg',instanceSide=side,articulation='independent complete biped leg; gait translation/rotation supplied by runtime')
    elif legs:
        reach={'corvus':.78,'atrax':.78,'spiroct':.92,'arkyid':1.02,'toxopid':1.08}[id]
        per=legs//2
        for side in [-1,1]:
            for j in range(per):
                fy=(j/(per-1)-.5) if per>1 else 0
                root=(center[0]+side*bw*.31,center[1]+fy*bh*.46)
                knee=(center[0]+side*bw*reach*.74,center[1]+fy*bh*1.18)
                foot=(center[0]+side*bw*reach,center[1]+fy*bh*1.55)
                idx=f'{"L" if side<0 else "R"}{j+1}'
                for name,a,b,role,region in [('leg-upper',root,knee,'leg_upper',f'{id}-leg'),('leg-lower',knee,foot,'leg_lower',f'{id}-leg-base')]:
                    meta=PARTS[name];anchor=meta['anchorPx']; end=[meta['width']*.5,meta['height']*.88];dist=math.dist(a,b);original=math.dist(anchor,end);scale=min(1,dist/original)
                    angle=math.degrees(math.atan2(b[0]-a[0],b[1]-a[1]))
                    add(name,role,a,scale,angle,engineRegion=region,legInstance=idx,endpointTargetPx=list(b),jointDesign='painted pivot integrated into segment; separate optional joint texture not required for this kit')
                fm=PARTS['leg-foot'];fscale=min(1,bw*.13/fm['width']);angle=math.degrees(math.atan2(foot[0]-knee[0],foot[1]-knee[1]))
                add('leg-foot','foot',foot,fscale,angle,engineRegion=f'{id}-foot',legInstance=idx)
    add(body,'body',center,1,engineRegion=id,bodyOnly=True)
    for index,(part,region,x,y,ww,rotate,officialXY) in enumerate(W.get(id,[])):
        pm=PARTS[part];dest=(center[0]+x*bw,center[1]+y*bh);scale=min(1,bw*ww/pm['width'])
        add(part,'weapon',dest,scale,engineRegion=region,weaponInstance=index,independentlyRotating=rotate,officialMountCoordinates=officialXY,coordinateNote='official world coordinates are source evidence; preview normalized positions are authored for redesigned body and require engine calibration')
    box=canvas.getbbox();pad=24;box=(box[0]-pad,box[1]-pad,box[2]+pad,box[3]+pad);im=canvas.crop(box)
    # Erase numerical RGB residue after resampling, without changing opaque painted shapes.
    ar=np.array(im);ar[ar[:,:,3]==0]=0;im=Image.fromarray(ar)
    for layer in layers:
        tr=layer['placement'];tr['targetAnchorPx']=[round(tr['targetAnchorPx'][0]-box[0],3),round(tr['targetAnchorPx'][1]-box[1],3)];tr['topLeft']=[tr['topLeft'][0]-box[0],tr['topLeft'][1]-box[1]]
        if 'endpointTargetPx' in layer:layer['endpointTargetPx']=[layer['endpointTargetPx'][0]-box[0],layer['endpointTargetPx'][1]-box[1]]
    p=OWN/'sprites'/f'{id}.png';im.save(p);gp=p.with_suffix('.png.generation.json')
    sources=[]
    for layer in layers:
        src={k:layer[k] for k in ['file','sha256','generationRecord']}
        if src not in sources:sources.append(src)
    stats=image_stats(im)
    record=dict(schemaVersion=1,file=rel(p),sha256=sha(p),createdAt=NOW,route='local-derived',tool='Python/Pillow',actualModel=None,actualQuality=None,derivedFrom=sources,operation=dict(type='authorized_layer_assembly_static_preview',noProgramDrawnArt=True,noUpscaling=True,canvasCrop=box,transforms=placements),image=stats,engineNotVerified=True)
    write(gp,record)
    layer_files=list(dict.fromkeys(l['file'] for l in layers))
    layer_mapping={}
    for l in layers:layer_mapping.setdefault(l['engineRegion'],[]).append(dict(file=l['file'],role=l['role'],instance=l.get('weaponInstance',l.get('legInstance',l.get('instanceSide')))))
    assets=dict(id=id,officialNameZhCN=u['officialNameZhCN'],file=rel(p),generationRecord=rel(gp),sha256=record['sha256'],width=im.width,height=im.height,role='compositePreview',forward='up / negative image y',anchorPx=[center[0]-box[0],center[1]-box[1]],bodyFile=body['file'],layers=layers,layerFiles=layer_files,layerMapping=layer_mapping,mobility=u['mobility'],family=u.get('family'),tierOrSequence=u.get('tierOrSequence'),officialDefinition=u['definition'],engineNotVerified=True,integrationStatus='art_layers_ready_engine_not_verified',articulation=dict(legCount=legs if legs else (2 if u['mobility']=='biped_mech' else 0),visibleWeaponMountCount=len(W.get(id,[]))),validation=dict(numeric=stats,visualReview='pending_final_contact_review',openIssues=[]))
    if id=='crawler':assets['layerMapping']['unnamed-suicide-weapon']=[dict(file=None,role='runtime-only ability; no external gun sprite',reason='Weapon() has no independent named sprite; self-detonation is runtime effect')]
    if id=='retusa':assets['layerMapping']['unnamed-torpedo-weapon']=[dict(file=None,role='runtime-only projectile launch; no independent named gun region')]
    if id=='aegires':assets['layerMapping']['EnergyFieldAbility']=[dict(file=body['file'],role='fixed central field motif integrated into body; radius effects are runtime')]
    ASSETS.append(assets)

manifest=dict(schemaVersion=1,worker='serpulo-ground-naval',release='v160.7',sourceCommit='17012d61d9e4c3cbd9820d87e81c24495486ac53',createdAt=NOW,scope=ids,excludedDelegated=['alpha','beta','gamma'],assetCount=len(ASSETS),assets=ASSETS,sharedParts=list(PARTS.values()),generationRecords=[s['generationRecord'] for s in SOURCES.values()],sourceImagesRetained=True,notes=['Images are generated hand-painted art with explicitly authorized local alpha cleanup/cropping/downsampling/mirroring/assembly.','Standalone layer files preserve native cropped pixels; assembled previews are not new model generations.','Layer anchor positions and sizes are authored art coordinates. Texture atlas packing, game-unit scale, animation/recoil and actual Mindustry loading have not been tested.','Optional base/joint overlays are incorporated in painted body/segment layers; runtime adapter may omit optional regions rather than duplicate opaque joints.','Color/energy beams, projectiles, water trails and procedural movement remain runtime effects; this unit kit supplies static body and motion/weapon parts.'])
write(OWN/'manifest.json',manifest)
write(REC/'crop-index.json',CROPS)

font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
for suffix,bg in [('light',(244,241,231)),('dark',(31,42,47)),('gray',(127,127,127))]:
    sheet=Image.new('RGB',(1800,1800),bg);d=ImageDraw.Draw(sheet)
    for i,a in enumerate(ASSETS):
        x=(i%5)*360;y=(i//5)*360;im=Image.open(ROOT/a['file']);im.thumbnail((340,315),Image.Resampling.LANCZOS);sheet.paste(im,(x+(360-im.width)//2,y+(320-im.height)//2),im)
        d.text((x+12,y+330),a['id'],font=font,fill='white' if suffix=='dark' else 'black')
    sheet.save(OWN/f'qa-{suffix}.jpg',quality=95)
print(json.dumps(dict(assetCount=len(ASSETS),bodyCount=len(BODIES),sharedParts=len(PARTS),ownPngCount=len(list(OWN.rglob('*.png'))),manifest=rel(OWN/'manifest.json')),ensure_ascii=False))
