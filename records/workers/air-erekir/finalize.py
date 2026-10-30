from pipeline import *
import re,math
BASE=json.loads((HERE/'manifest.json').read_text(encoding='utf-8'))
BODIES={a['id']:a for a in json.loads((HERE/'body-layers.json').read_text(encoding='utf-8'))}
PARTS={a['id']:a for a in json.loads((ROOT/'records/workers/air-erekir-parts/manifest.json').read_text(encoding='utf-8'))['assets']}
JAVA=(ROOT/'records/reference-unit-sources/UnitTypes.java').read_text(encoding='utf-8')
SOURCE={a['name']:a for a in json.loads((HERE/'source-summary.json').read_text(encoding='utf-8'))}
LEGS={'merui':(6,'short'),'cleroi':(4,'short'),'anthicus':(6,'medium'),'tecta':(6,'heavy'),'collaris':(8,'heavy')}
TANKS=['stell','locus','precept','vanquish','conquer']
# Visual mount positions in normalized body coordinates, x-right / y-down. Independent of game-world offsets.
GUNS={
'zenith':[('zenith-missiles',.27,.47,.27),('zenith-missiles',.73,.47,.27)],
'antumbra':[('missiles-mount',.22,.38,.20),('missiles-mount',.78,.38,.20),('missiles-mount',.22,.67,.20),('missiles-mount',.78,.67,.20),('large-bullet-mount',.39,.45,.17),('large-bullet-mount',.61,.45,.17)],
'eclipse':[('large-laser-mount',.36,.5,.20),('large-laser-mount',.64,.5,.20),('large-artillery',.21,.39,.16),('large-artillery',.79,.39,.16),('large-artillery',.19,.68,.16),('large-artillery',.81,.68,.16)],
'mega':[('heal-weapon-mount',.21,.60,.15),('heal-weapon-mount',.79,.60,.15),('heal-weapon-mount',.35,.31,.13),('heal-weapon-mount',.65,.31,.13)],
'incite':[('build-weapon',.28,.34,.18),('build-weapon',.72,.34,.18)],
'quell':[('quell-weapon',.25,.32,.33),('quell-weapon',.75,.32,.33)],
'disrupt':[('disrupt-weapon',.30,.32,.28),('disrupt-weapon',.70,.32,.28)],
'stell':[('stell-weapon',.5,.45,.50)],'locus':[('locus-weapon',.5,.48,.52)],'precept':[('precept-weapon',.5,.50,.54)],
'vanquish':[('vanquish-weapon',.5,.52,.50),('vanquish-point-weapon',.24,.25,.19),('vanquish-point-weapon',.76,.25,.19),('vanquish-point-weapon',.24,.75,.19),('vanquish-point-weapon',.76,.75,.19)],
'conquer':[('conquer-weapon',.5,.48,.61)],
'merui':[('merui-weapon',.5,.32,.40)],
'cleroi':[('cleroi-weapon',.30,.35,.28),('cleroi-weapon',.70,.35,.28),('cleroi-point-defense',.32,.69,.18),('cleroi-point-defense',.68,.69,.18)],
'anthicus':[('anthicus-weapon',.23,.56,.38),('anthicus-weapon',.77,.56,.38)],
'tecta':[('tecta-weapon',.23,.48,.30),('tecta-weapon',.77,.48,.30)],
'collaris':[('collaris-weapon',.28,.53,.27),('collaris-weapon',.72,.53,.27)]}
AUX={
'conquer':[('conquer-glow','conquer-weapon','alpha_tinted_additive',1),('conquer-weapon-glow','conquer-weapon','alpha_tinted_additive',1),('conquer-weapon-sides','disrupt-tail','mirrored_side_blade',2),('conquer-weapon-sinks','track-strip','mirrored_heat_sink',2),('conquer-weapon-sinks-heat','track-strip','alpha_tinted_additive',2),('conquer-weapon-blade','disrupt-tail','three_mirrored_pairs',6)],
'cleroi':[('cleroi-spine','disrupt-tail','five_mirrored_pairs',10)],
'anthicus':[('anthicus-blade','disrupt-tail','three_mirrored_pairs',6),('anthicus-weapon-blade','disrupt-tail','two_mirrored_pairs_per_weapon',8)],
'collaris':[('collaris-weapon-blade','disrupt-tail','five_per_weapon',10)],
'obviate':[('obviate-blade','disrupt-tail','mirrored_body_blade',2),('obviate-side','disrupt-tail','mirrored_child_side',4)],
'disrupt':[('disrupt-weapon-blade','disrupt-tail','mirrored_per_weapon',4)],
'tecta':[('tecta-shield','tecta-shield','optional_ability_visual_not_engine_region',1)]}
def source_block(id):
 start=JAVA.index('        '+id+' = new ');end=JAVA.find('\n        ',start+10)
 nxt=re.search(r'\n        \w+ = new \w+\(',JAVA[start+10:]);return JAVA[start:start+10+nxt.start()] if nxt else JAVA[start:]
def canonical_weapons(id):
 text=source_block(id);out=[]
 for m in re.finditer(r'new (\w*Weapon)\("([^"]+)"\)\s*\{\{',text):
  tail=text[m.end():];end=tail.find('bullet =');prefix=tail[:end] if end>=0 else tail[:tail.find('}}')]
  prefix=prefix.split('parts.add')[0]
  props={}
  for key in ['x','y','mirror','rotate','baseRotation','rotationLimit','layerOffset','shootY']:
   v=re.search(r'(?m)^\s*'+key+r'\s*=\s*([^;]+);',prefix)
   props[key]=v.group(1).strip() if v else None
  if id=='vanquish' and m.group(2)=='vanquish-point-weapon':props['loopValues']={'y':['34f / 4f','-36f / 4f']}
  out.append(dict(region=m.group(2),type=m.group(1),sourceExpressions=props,worldSpace='Mindustry world units, x-right/y-forward; raw source expressions, not art pixels'))
 return out
def part_layer(name,role='weapon'):
 p=PARTS[name];return dict(file=p['file'],role=role,region=name,generationRecord=p['record'],sha256=p['sha256'],size=p['outputSize'],pivotPixels=p['pivot'],pivotStatus='visual_estimate',facing=p['forward'],engineNotVerified=True)
def make_assembly(id,body):
 canvas=Image.new('RGBA',(1400,1400));placements=[];src=Image.open(ROOT/body['file']).convert('RGBA');bs=min(1,470/max(src.size));bw,bh=[round(v*bs) for v in src.size];origin=(700-bw/2,700-bh/2)
 def put(file,pivot,anchor,scale=1,rot=0,mirror=False,role='part',region=None):
  im=Image.open(ROOT/file).convert('RGBA');scale=min(scale,1);ow,oh=im.size;nw,nh=max(1,round(ow*scale)),max(1,round(oh*scale));im=im.resize((nw,nh),Image.Resampling.LANCZOS);px,py=pivot[0]*nw/ow,pivot[1]*nh/oh
  if mirror:im=im.transpose(Image.Transpose.FLIP_LEFT_RIGHT);px=nw-px
  if rot:
   ang=math.radians(rot);dx,dy=px-nw/2,py-nh/2;im=im.rotate(-rot,Image.Resampling.BICUBIC,expand=True);px=im.width/2+math.cos(ang)*dx-math.sin(ang)*dy;py=im.height/2+math.sin(ang)*dx+math.cos(ang)*dy
  xy=(round(anchor[0]-px),round(anchor[1]-py));canvas.alpha_composite(im,xy)
  placements.append(dict(file=file,role=role,region=region,anchorPixels=list(anchor),scale=scale,rotationClockwise=rot,mirrorX=mirror,pivotSourcePixels=pivot))
 def pos(x,y):return (origin[0]+x*bw,origin[1]+y*bh)
 def pp(name,xy,widthRatio,role='weapon',rot=0,mirror=False):
  p=PARTS[name];scale=min(1,bw*widthRatio/p['nativeExtractedSize'][0]);put(p['file'],p['pivot'],xy,scale,rot,mirror,role,name)
 if id in LEGS:
  count,tier=LEGS[id];pairs=count//2;ys=np.linspace(.25,.75,pairs)
  for side in [-1,1]:
   for i,yy in enumerate(ys):
    root=pos(.5+side*.30,float(yy));bend=-.17 if yy<.45 else (.17 if yy>.55 else .10);knee=pos(.5+side*.53,float(yy+bend));foot=pos(.5+side*.73,float(yy+bend*.3))
    for suffix,a,b in [('upper',root,knee),('lower',knee,foot)]:
     p=PARTS[f'leg-{tier}-{suffix}'];j0,j1=p['jointCenters'];native=math.dist(j0,j1);wanted=math.dist(a,b);rot=math.degrees(math.atan2(b[1]-a[1],b[0]-a[0]))-90;put(p['file'],j0,a,min(1,wanted/native),rot,side<0,'leg_'+suffix,p['id'])
    pp('foot-'+tier,foot,.14,'foot',rot=side*80,mirror=side<0)
 if id=='disrupt':
  pp('disrupt-tail',pos(.34,.64),.31,'designed_rear_wing',mirror=False);pp('disrupt-tail',pos(.66,.64),.31,'designed_rear_wing',mirror=True)
 put(body['file'],[src.width/2,src.height/2],(700,700),bs,role='body',region=id)
 for name,x,y,width in GUNS.get(id,[]):pp(name,pos(x,y),width)
 # Movable blade designs are reusable modules. The parked pose stays compact; full warmup articulation is an engine concern.
 if id in ['cleroi','anthicus']:
  qty={'cleroi':5,'anthicus':3}[id]
  for side in [-1,1]:
   for k in range(qty):pp('disrupt-tail',pos(.5+side*.38,.28+k*.11),.10,'auxiliary_blade',rot=-35*side,mirror=side>0)
 if id=='obviate':
  pp('disrupt-tail',pos(.39,.55),.19,'auxiliary_blade');pp('disrupt-tail',pos(.61,.55),.19,'auxiliary_blade',mirror=True)
 b=canvas.getbbox();canvas=canvas.crop((max(0,b[0]-32),max(0,b[1]-32),min(1400,b[2]+32),min(1400,b[3]+32)));offset=(max(0,b[0]-32),max(0,b[1]-32))
 arr=np.array(canvas);arr[:,:,3][arr[:,:,3]<8]=0;arr[arr[:,:,3]==0,:3]=0;canvas=Image.fromarray(arr)
 for p in placements:p['anchorPixels']=[round(p['anchorPixels'][0]-offset[0],3),round(p['anchorPixels'][1]-offset[1],3)]
 target=ROOT/'units/air-erekir/assembled'/(id+'.png');target.parent.mkdir(parents=True,exist_ok=True);canvas.save(target)
 refs=[]
 for p in placements:
  if p['file'] in [r['file'] for r in refs]:continue
  r=body if p['file']==body['file'] else next(v for v in PARTS.values() if v['file']==p['file']);refs.append(dict(file=p['file'],sha256=sha(ROOT/p['file']),generationRecord=r.get('generationRecord',r.get('record'))))
 rec=dict(schemaVersion=1,file=target.relative_to(ROOT).as_posix(),sha256=sha(target),width=canvas.width,height=canvas.height,format='PNG',mode='RGBA',derivedFrom=refs,operation={'type':'assembly_of_native_generated_layers','noUpsampling':True,'placements':placements,'note':'Downsampling, mirroring, rotation and alpha compositing only; no procedural drawing.'},facing='north',actualModel=None,actualQuality=None,engineRuntimeVerified=False)
 write(target.with_name(target.name+'.generation.json'),rec)
 return rec,placements,[round(700-offset[0],3),round(700-offset[1],3)]
assets=[]
for old in BASE['assets']:
 id=old['id'];body=BODIES.get(id)
 if not body:
  original='units/air-erekir/individual/'+id+'.png';originalRecord=json.loads((ROOT/(original+'.generation.json')).read_text(encoding='utf-8'))
  body=dict(id=id,file=original,role='body_with_fixed_equipment',generationRecord=original+'.generation.json',sha256=sha(ROOT/original),size=[originalRecord['width'],originalRecord['height']],anchorNormalized=[.5,.5],facing='north',completeUnderpaint=True)
 layers=[body];mapping=[dict(engineRegion=id,file=body['file'],role='body',reuse=False)];names=sorted(set(g[0] for g in GUNS.get(id,[])))
 for name in names:
  layers.append(part_layer(name));mapping.append(dict(engineRegion=name,file=PARTS[name]['file'],role='weapon',instances=sum(g[0]==name for g in GUNS[id]),reuse='mirror/repeat same native region',canonicalSource=[v for v in canonical_weapons(id) if v['region']==name]))
 if id in LEGS:
  count,tier=LEGS[id]
  for region,name in [('leg','leg-'+tier+'-upper'),('leg-base','leg-'+tier+'-lower'),('foot','foot-'+tier)]:
   layers.append(part_layer(name,'articulated_'+region));mapping.append(dict(engineRegion=id+'-'+region,file=PARTS[name]['file'],instances=count,reuse='shared '+tier+' limb kit, mirrored for opposite side',jointCenters=PARTS[name]['jointCenters']))
  mapping+= [dict(engineRegion=id+'-joint',file=PARTS['leg-'+tier+'-upper']['file'],reuse='joint is integrated in upper segment; suppress additional joint sprite in adapter',adapterAction='do_not_draw_duplicate_joint'),dict(engineRegion=id+'-joint-base',file=PARTS['leg-'+tier+'-lower']['file'],reuse='joint is integrated in lower segment; suppress additional joint sprite in adapter',adapterAction='do_not_draw_duplicate_joint')]
 if id in TANKS:
  layers.append(part_layer('track-strip','tread_animation_source'));mapping.append(dict(engineRegion=id+'-treads',file=PARTS['track-strip']['file'],reuse='repeat mirrored tread texture into per-hull treadRects; authored chassis includes static neutral tracks',adapterAction='mask tread cycle to authored chassis track area'))
 for official,name,reuse,count in AUX.get(id,[]):
  if PARTS[name]['file'] not in [l['file'] for l in layers]:layers.append(part_layer(name,'motion_or_effect_part'))
  mapping.append(dict(engineRegion=official,file=PARTS[name]['file'],reuse=reuse,instances=count,adapterAction='use alpha as tint mask' if 'alpha_' in reuse else 'mount and animate reusable painted module'))
 # Named fixed equipment is represented inside the body; runtime adapter suppresses duplicate region draws.
 for w in canonical_weapons(id):
  if not any(m['engineRegion']==w['region'] for m in mapping):mapping.append(dict(engineRegion=w['region'],file=body['file'],reuse='fixed equipment integrated in body',adapterAction='suppress duplicate region draw; keep muzzle and gameplay behavior',canonicalSource=w))
 if id in BODIES or id=='obviate':
  rec,placements,anchor=make_assembly(id,body);file=rec['file'];record=file+'.generation.json';size=[rec['width'],rec['height']];digest=rec['sha256']
 else:file=old['file'];record=old['generationRecord'];size=old['size'];digest=old['sha256'];placements=[];anchor=[size[0]/2,size[1]/2]
 a=dict(id=id,file=file,generationRecord=record,sha256=digest,size=size,compositePreview=file,layers=layers,layerFiles=list(dict.fromkeys(l['file'] for l in layers)),layerMapping=mapping,assembly=placements,bodyAnchorPixels=anchor,facing='north',originalName=id,canonicalSource=SOURCE[id],officialWeaponOffsets=canonical_weapons(id),legCount=LEGS.get(id,(0,None))[0],status='art_exported_pending_final_visual_check',engineNotVerified=True,coordinateNote='assembly anchorPixels are estimated art pixels; officialWeaponOffsets are original game-world expressions and must not be substituted for pixels.')
 assets.append(a)
write(HERE/'manifest.json',dict(schemaVersion=1,worker='air-erekir',updatedAt=datetime.now(timezone.utc).isoformat(),status='assembled_pending_final_visual_check',assets=assets,uniqueRequiredUnitIds=28,bodyLayerCount=28,independentRedrawnBodies=17,sharedPartsManifest='records/workers/air-erekir-parts/manifest.json',engineNotVerified=True))
# Export one proof sheet: each actual final PNG on light / dark / gray split backgrounds.
thumb=270;cols=7;rows=4;sheet=Image.new('RGB',(cols*290,rows*315),(235,229,213));d=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for i,a in enumerate(assets):
 im=Image.open(ROOT/a['file']).convert('RGBA');im.thumbnail((thumb,thumb),Image.Resampling.LANCZOS);tile=Image.new('RGBA',(thumb,thumb));td=ImageDraw.Draw(tile)
 for k,c in enumerate([(244,239,222,255),(31,42,42,255),(124,124,124,255)]):td.rectangle((k*90,0,k*90+89,thumb),fill=c)
 tile.alpha_composite(im,((thumb-im.width)//2,(thumb-im.height)//2));x=i%cols*290+10;y=i//cols*315+10;sheet.paste(tile.convert('RGB'),(x,y));d.text((x,y+276),a['id'],font=font,fill=(20,60,50))
sheet.save(ROOT/'units/air-erekir/final-contact.png');write(HERE/'final-contact.json',dict(file='units/air-erekir/final-contact.png',sha256=sha(ROOT/'units/air-erekir/final-contact.png'),operation='downsampled QA contact of final alpha composites on ivory/dark/gray',sources=[dict(file=a['file'],sha256=a['sha256']) for a in assets]))
print(json.dumps({'units':len(assets),'assemblies':sum(bool(a['assembly']) for a in assets),'layerReferences':sum(len(a['layers']) for a in assets)}))
