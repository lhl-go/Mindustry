from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageChops
import json,hashlib,re,shutil,base64,math,numpy as np
from datetime import datetime,timezone
B=Path(__file__).resolve().parents[1];R=B.parents[1];P=R.parent
rd=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rel=lambda p:Path(p).relative_to(R).as_posix()
def wr(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def record_path(p):
 for s in ['.generation.json','.derived.json','.source.json']:
  q=Path(str(p)+s)
  if q.exists():return rel(q)
 return None
def srcinfo(p):return dict(file=rel(p),sha256=sha(p),generationRecord=record_path(p))
def ingest_parts():
 j=rd(B/'unit-bases-joints.receipt.json');old=Path(re.search(r' as (C:.*?\.png) by default',j['result']['output_hint']).group(1));src=B/'source/unit-bases-joints.png';src.parent.mkdir(exist_ok=True);shutil.copyfile(old,src);im=Image.open(src).convert('RGBA');prompt=B/'unit-bases-joints.prompt.txt';prompt.write_text(j['args']['prompt'],encoding='utf-8');wr(Path(str(src)+'.generation.json'),dict(file=rel(src),sha256=sha(src),generatedAt=j['returnedAt'],startedAt=j['startedAt'],tool='image_gen.imagegen',route='builtin',width=im.width,height=im.height,format='PNG',mode='RGBA',configSnapshot=rd(P/'config/image-generation.json'),submittedParameters=dict(model=None,quality=None,**j['args']),actualModel=None,actualQuality=None,unverifiedReason='Host managed; builtin tool does not expose model/quality selectors or actual snapshot metadata.',prompt=rel(prompt),references=[dict(file=x,sha256=sha(x),purpose='primary_style_reference',actuallyAttached=True) for x in j['args']['referenced_image_paths']],evidence=dict(receipt=rel(B/'unit-bases-joints.receipt.json'),outputHint=j['result']['output_hint']),sourceImageRetained=True))
 boxes=[[0,0,450,490],[450,0,1070,490],[1070,0,1536,490],[0,490,450,1024],[450,490,1000,1024],[1000,490,1536,1024]];parts={}
 for id,box in zip(j['names'],boxes):
  a=np.array(im.crop(box));al=a[:,:,3];al[al<16]=0;al[al>=245]=255;a[al==0,:3]=0;cut=Image.fromarray(a);bb=cut.getbbox();cut=cut.crop(bb);out=Image.new('RGBA',(cut.width+32,cut.height+32));out.alpha_composite(cut,(16,16));p=B/'parts'/f'{id}.png';p.parent.mkdir(exist_ok=True);out.save(p);wr(Path(str(p)+'.generation.json'),dict(file=rel(p),sha256=sha(p),width=out.width,height=out.height,mode='RGBA',format='PNG',derivedFrom=[srcinfo(src)],operation=dict(type='native_crop_alpha_cleanup',crop=box,trim=list(bb),padding=16,alphaBelow16ToZero=True,alphaAtLeast245To255=True),upsampled=False,actualModel=None,actualQuality=None,unverifiedReason='Derived from recorded builtin generation; actual model/quality not disclosed.'));parts[id]=rel(p)
 return parts
def references(audit):
 for fp in B.glob('*.png.fetch.json'):
  j=rd(fp);data=base64.b64decode(j['content']);p=B/'reference'/j['sourcePath'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 rows=[]
 for x in audit['assets']:
  p=B/'reference'/x['sourcePath'];data=p.read_bytes();blob=hashlib.sha1(('blob '+str(len(data))+'\0').encode()+data).hexdigest();assert blob==x['sourceGitBlob'],x['region'];im=Image.open(p).convert('RGBA');bb=im.getbbox();rows.append({**x,'localReference':rel(p),'sourceDimensions':list(im.size),'sourceAlphaBounds':list(bb) if bb else None,'sourceSha256':sha(p)})
 wr(B/'source-inventory.json',dict(assets=rows,errors=[]));return {a['region']:a for a in rows}
def all_manifests():
 names=['records/workers/special/manifest.json','units/serpulo-ground-naval/manifest.json','records/workers/root-builders/manifest.json','records/workers/air-erekir/manifest.json','records/workers/air-erekir-parts/manifest.json','records/workers/serpulo-root-parts/manifest.json']
 return [(n,rd(R/n)) for n in names]
def known_data():
 anchors={};consumers={};composites={}
 for name,m in all_manifests():
  for a in m.get('assets',[]):
   if a.get('id') and a.get('file'):composites[a['id']]=a['file']
   if isinstance(a.get('pivot'),list):anchors[a['file']]=a['pivot']
   maps=a.get('layerMapping') or []
   if isinstance(maps,dict):items=[(k,x) for k,ls in maps.items() for x in ls]
   else:items=[(l.get('engineRegion'),l) for l in maps]
   for region,l in items:
    if region:consumers.setdefault(region,[]).append(dict(assetId=a.get('id'),manifest=name,file=l.get('file')))
   for l in a.get('layers') or []:
    if not isinstance(l,dict):continue
    p=l.get('file');anchor=l.get('anchorPx') or l.get('pivotPixels')
    if not anchor and isinstance(l.get('pivot'),list):anchor=l['pivot']
    if not anchor and l.get('anchorNormalized') and p:
     im=Image.open(R/p);anchor=[l['anchorNormalized'][0]*im.width,l['anchorNormalized'][1]*im.height]
    if p and anchor:anchors[p]=anchor
 return anchors,consumers,composites
def alias_map(parts,existing,composites):
 out={}
 def put(region,file,role,reason):out[region]=dict(file=file,sha256=sha(R/file),manifest='full-game/units/manifest.json',role=role,selectionReason=reason)
 for unit in ['dagger','mace','fortress','nova','pulsar','quasar']:put(unit+'-base',parts['mech-base-small'],'underbody_base','Shared complete small hip base, independently drawn beneath unit; native painted part reused at official region dimensions.')
 for unit in ['scepter','reign','vela','corvus']:put(unit+'-base',parts['mech-base-heavy'],'underbody_base','Shared complete heavy hip base; preserve official underbody draw and frame center.')
 for unit in ['crawler','atrax']:put(unit+'-base',parts['crawler-base-plate'],'underbody_base','Complete compact crawler underbody plate reused beneath the actual source-defined limbs.')
 for unit in ['atrax','spiroct']:put(unit+'-joint',parts['joint-cap-small'],'joint','Complete independent joint cap; no leg was hard-cropped.')
 put('corvus-joint',parts['joint-cap-heavy'],'joint','Complete heavy independent cap.')
 for unit in ['arkyid','toxopid','corvus']:put(unit+'-joint-base',parts['joint-socket'],'joint_base','Complete painted socket reused for source leg-root positions.')
 put('disrupt-missile-fin','units/special/layers/disrupt-missile-left-fin.png','region_part','Canonical single fin is reused/mirrored by the source RegionPart; the right-fin image remains design evidence only.')
 put('obviate-preview',composites['obviate'],'composite_preview','Complete existing assembled obviate is used for the named static preview only.')
 put('incite-weapon','units/air-erekir-parts/assets/build-weapon.png','weapon','Compatibility alias of the complete builder weapon; UnitTypes incite currently instantiates BuildWeapon("build-weapon").')
 put('repair-beam-weapon','units/air-erekir-parts/assets/heal-weapon-mount.png','weapon','Complete repair emitter reused for generic repair-beam weapon atlas name.')
 put('small-weapon','units/root-builders/layers/small-basic-weapon.png','weapon','Generic legacy small weapon region reuses the complete small cannon module.')
 put('weapon','units/serpulo-ground-naval/parts/mech-autocannon.png','weapon','Generic default weapon region reuses the complete autocannon module.')
 # Resolve global shared atlas names once rather than emit conflicting images for the same region.
 for region in ['large-bullet-mount','missiles-mount','large-artillery']:put(region,f'units/air-erekir-parts/assets/{region}.png','weapon','Canonical global atlas selection: one complete named air/ground-compatible module serves every consumer. Frozen illustrative compositions are not overwritten.')
 # A weapon preview contains its moving blades in their authored neutral pose; it is never used as the runtime weapon body.
 gun=Image.open(R/'units/air-erekir-parts/assets/disrupt-weapon.png').convert('RGBA');blade=Image.open(R/'units/air-erekir-parts/assets/disrupt-tail.png').convert('RGBA');canvas=Image.new('RGBA',(800,650));blade.thumbnail((260,260),Image.Resampling.LANCZOS);canvas.alpha_composite(blade,(28,220));canvas.alpha_composite(blade.transpose(Image.Transpose.FLIP_LEFT_RIGHT),(800-blade.width-28,220));gun.thumbnail((490,420),Image.Resampling.LANCZOS);canvas.alpha_composite(gun,((800-gun.width)//2,(650-gun.height)//2));p=B/'parts/disrupt-weapon-preview.png';canvas.save(p);wr(Path(str(p)+'.generation.json'),dict(file=rel(p),sha256=sha(p),width=800,height=650,format='PNG',mode='RGBA',derivedFrom=[srcinfo(R/'units/air-erekir-parts/assets/disrupt-weapon.png'),srcinfo(R/'units/air-erekir-parts/assets/disrupt-tail.png')],operation='static neutral-pose composite: independent weapon and two mirrored native blades; local downsampling, no generated art added',upsampled=False,actualModel=None,actualQuality=None,unverifiedReason='Composition of traced images.'));put('disrupt-weapon-preview',rel(p),'composite_preview','Static assembled weapon preview; runtime gun and blades remain separate atlas regions.')
 return out
LINE_UNITS={'anthicus','arkyid','atrax','cleroi','collaris','corvus','merui','spiroct','tecta','toxopid'}
TREADS={'stell':{'rects':[[-20,-25,14,51]],'pull':3},'locus':{'rects':[[-31,-38,19,76]],'pull':5},'precept':{'rects':[[-44,-22,30,75],[-16,-53,17,60]],'pull':5},'vanquish':{'rects':[[-55,-61,28,130]],'pull':4},'conquer':{'rects':[[-88.5,36.5,56,73],[-91.5,-73.5,29,17],[-56.5,-106.5,39,19]],'pull':1}}
def export_region(region,row,mapping,anchors):
 src=R/mapping['file'];im=Image.open(src).convert('RGBA');size=row['sourceDimensions'];bb=im.getbbox();crop=im.crop(bb);nativePivot=anchors.get(mapping['file']);rotation=0;op='native art downsample and register to original alpha bounds'
 unit=region.split('-leg')[0];isLine=unit in LINE_UNITS and (region.endswith('-leg') or region.endswith('-leg-base'))
 if isLine:crop=crop.transpose(Image.Transpose.ROTATE_90);rotation=90;op='rotate native limb 90deg CCW so its long axis follows Lines.line U/x axis; downsample to original line texture bounds'
 box=row['sourceAlphaBounds'] or [0,0,*size]
 if mapping['role'] in ['body','head','tail','torso']:box=[min(4,size[0]//10),min(4,size[1]//10),size[0]-min(4,size[0]//10),size[1]-min(4,size[1]//10)]
 limit=[max(1,box[2]-box[0]),max(1,box[3]-box[1])];out=Image.new('RGBA',tuple(size))
 if mapping['role']=='weapon' and nativePivot:
  pivot=[nativePivot[0]-bb[0],nativePivot[1]-bb[1]];pivot=[min(max(pivot[0],0),crop.width),min(max(pivot[1],0),crop.height)];ext=[max(pivot[0],crop.width-pivot[0]),max(pivot[1],crop.height-pivot[1])];s=min(1,(size[0]/2-1)/max(ext[0],1),(size[1]/2-1)/max(ext[1],1));crop=crop.resize((max(1,round(crop.width*s)),max(1,round(crop.height*s))),Image.Resampling.LANCZOS);pos=[round(size[0]/2-pivot[0]*s),round(size[1]/2-pivot[1]*s)];out.alpha_composite(crop,tuple(pos));op='native painted weapon pivot registered to original region center; bounded downsampling';anchorOut=[size[0]/2,size[1]/2]
 else:
  crop.thumbnail(tuple(limit),Image.Resampling.LANCZOS);pos=[round((box[0]+box[2]-crop.width)/2),round((box[1]+box[3]-crop.height)/2)];out.alpha_composite(crop,tuple(pos));s=None;anchorOut=[size[0]/2,size[1]/2]
 arr=np.array(out);arr[arr[:,:,3]==0,:3]=0;out=Image.fromarray(arr);p=B/'engine'/row['sourcePath'];p.parent.mkdir(parents=True,exist_ok=True);out.save(p)
 rec=dict(file=rel(p),sha256=sha(p),width=size[0],height=size[1],mode='RGBA',format='PNG',derivedFrom=[srcinfo(src)],operation=dict(type='engine_atlas_export',description=op,sourceTrim=list(bb),sourcePivot=nativePivot,rotationDegreesCCW=rotation,destinationTopLeft=pos,sourceDimensions=list(im.size),targetDimensions=size,officialAlphaBounds=box,scale=s,engineAnchorPx=anchorOut),officialSource=dict(path=row['sourcePath'],gitBlobSha1=row['sourceGitBlob'],sha256=row['sourceSha256']),upsampled=False,actualModel=None,actualQuality=None,unverifiedReason='Derived from recorded native art; no new generation call.',engineNotVerified=True);wr(Path(str(p)+'.generation.json'),rec);return dict(file=rel(p),sha256=sha(p),generationRecord=rel(p)+'.generation.json',size=size,engineAnchorPx=anchorOut,nativeFile=mapping['file'],nativeGenerationRecord=record_path(src),role=mapping['role'],sourceMapping=mapping,registration=rec['operation'])
def mask_export(region,row,exported,rows):
 kind='heat' if region.endswith('-heat') else 'glow' if region.endswith('-glow') else 'cell';base=region[:-5]
 if region=='power-cell':
  source=R/'full-game/items-fx/assets/circle-bullet.png';im=Image.open(source).convert('RGBA');im=im.crop(im.getbbox());im.thumbnail(tuple(row['sourceDimensions']),Image.Resampling.LANCZOS);body=Image.new('RGBA',tuple(row['sourceDimensions']));body.alpha_composite(im,((body.width-im.width)//2,(body.height-im.height)//2));prepared=B/'mask-bases/power-cell-base.png';prepared.parent.mkdir(exist_ok=True);body.save(prepared);wr(Path(str(prepared)+'.generation.json'),dict(file=rel(prepared),sha256=sha(prepared),format='PNG',mode='RGBA',width=body.width,height=body.height,derivedFrom=[srcinfo(source)],operation='downsample and center the recorded jade pearl to generic fallback cell canvas; art remains traced',upsampled=False,actualModel=None,actualQuality=None,unverifiedReason='Local export from traced generated art.'));base='global-fallback-jade-pearl';baseFile=rel(prepared);baseSize=list(body.size)
 else:
  assert base in exported,(region,base);baseFile=exported[base]['file'];body=Image.open(R/baseFile).convert('RGBA');baseSize=list(body.size)
 a=np.array(body).astype('float32');rgb=a[:,:,:3];al=a[:,:,3];r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2];bbox=body.getbbox();yy,xx=np.mgrid[:body.height,:body.width]
 if kind=='cell':
  color=(g>r*1.06)&(g>b*.90)&(g>55);cx=(bbox[0]+bbox[2])/2;cy=(bbox[1]+bbox[3])/2;domain=(abs(xx-cx)<(bbox[2]-bbox[0])*.32)&(abs(yy-cy)<(bbox[3]-bbox[1])*.38);sel=color&domain&(al>=128)
 else:sel=(r>g*.96)&(g>b*1.15)&(g>125)&(al>=128)
 fallback=False
 if int(sel.sum())<max(1,int(np.count_nonzero(al)*.003)):
  # A compact center patch is clipped from existing painted opaque pixels; never invent a floating old silhouette.
  fallback=True;cx=(bbox[0]+bbox[2])/2;cy=(bbox[1]+bbox[3])/2;sel=(abs(xx-cx)<max(1,(bbox[2]-bbox[0])*.14))&(abs(yy-cy)<max(1,(bbox[3]-bbox[1])*.16))&(al>=128)
  if not sel.any():sel=al>=128
 mask=np.zeros_like(a,dtype='uint8');mask[:,:,:3]=255;mask[:,:,3]=np.where(sel,al,0).astype('uint8');mask[mask[:,:,3]==0,:3]=0;small=Image.fromarray(mask);out=Image.new('RGBA',tuple(row['sourceDimensions']));off=[round((out.width-body.width)/2),round((out.height-body.height)/2)];out.alpha_composite(small,tuple(off));p=B/'engine'/row['sourcePath'];p.parent.mkdir(parents=True,exist_ok=True);out.save(p)
 rec=dict(file=rel(p),sha256=sha(p),width=out.width,height=out.height,format='PNG',mode='RGBA',derivedFrom=[srcinfo(R/baseFile)],operation=dict(type='new_shape_aligned_white_'+kind+'_mask',baseRegion=base,baseCanvas=baseSize,outputCanvas=list(out.size),centerRegistrationOffset=off,colorSelection='central existing jade pixels' if kind=='cell' else 'existing warm-gold illuminated surface pixels',fallbackToClippedCentralOpaquePatch=fallback,preservesOriginalMaskPixels=False,whiteRgb=True,alphaLimitedToNewBody=True),officialSource=dict(path=row['sourcePath'],gitBlobSha1=row['sourceGitBlob'],sha256=row['sourceSha256']),runtime=dict(function='UnitType.drawCell/cellColor' if kind=='cell' else 'Weapon/RegionPart heat draw',tint='runtime team/health color' if kind=='cell' else 'source-defined heatColor * recoil/warmup',geometry='same unit/part center; canvas differences accounted for'),actualModel=None,actualQuality=None,unverifiedReason='Pixel-derived mask from traced new art; no image model call.',engineNotVerified=True);wr(Path(str(p)+'.generation.json'),rec)
 return dict(file=rel(p),sha256=sha(p),generationRecord=rel(p)+'.generation.json',size=list(out.size),engineAnchorPx=[out.width/2,out.height/2],nativeFile=baseFile,nativeGenerationRecord=record_path(R/baseFile),role=kind+'_mask',maskBaseRegion=base,maskBaseFile=baseFile,maskRegistrationOffset=off,maskFallback=fallback,maskDerivation=rec['operation'])
def treads(row):
 unit=row['region'].replace('-treads','');spec=TREADS[unit];src=R/'units/air-erekir-parts/assets/track-strip.png';native=Image.open(src).convert('RGBA');native=native.crop(native.getbbox());size=row['sourceDimensions'];out=Image.new('RGBA',tuple(size));placements=[]
 for rect in spec['rects']:
  x,y,w,h=rect;x=int(x+size[0]/2);y=int(y+size[1]/2);track=native.resize((w,h),Image.Resampling.LANCZOS)
  # The official generator samples x==rect.left. Use the actual painted belt center-column for that one-pixel animation strip.
  center=track.crop((w//2,0,w//2+1,h));track.paste(center,(0,0));out.alpha_composite(track,(x,y));mirror=track.transpose(Image.Transpose.FLIP_LEFT_RIGHT);out.alpha_composite(mirror,(size[0]-x-w,y));placements.append(dict(left=[x,y,w,h],right=[size[0]-x-w,y,w,h],sampleColumnFromNativeBeltCenter=True))
 p=B/'engine'/row['sourcePath'];out.save(p);op=dict(type='paired_tread_canvas_from_native_track_component',placements=placements,officialTreadRects=spec['rects'],cropAndDownsampleOnly=True,sourceFrames=18,sourceTreadPullOffset=spec['pull']);wr(Path(str(p)+'.generation.json'),dict(file=rel(p),sha256=sha(p),width=out.width,height=out.height,format='PNG',mode='RGBA',derivedFrom=[srcinfo(src)],operation=op,officialSource=dict(path=row['sourcePath'],sha256=row['sourceSha256'],gitBlobSha1=row['sourceGitBlob']),actualModel=None,actualQuality=None,unverifiedReason='Local assembly from traced native tread strip.',engineNotVerified=True));generated=[]
 for n,rect in enumerate(spec['rects']):
  x=int(rect[0]+size[0]/2);y=int(rect[1]+size[1]/2);h=rect[3];sl=out.crop((x,y,x+1,y+h));arr=np.array(sl)
  for i in range(18):
   indices=np.arange(h)+i;indices=np.where(indices>=h,(indices-h+spec['pull'])%h,indices);frame=Image.fromarray(arr[indices]);dst=B/'generated-atlas'/f'{unit}-treads{n}-{i}.png';dst.parent.mkdir(exist_ok=True);frame.save(dst);wr(Path(str(dst)+'.generation.json'),dict(file=rel(dst),sha256=sha(dst),width=1,height=h,format='PNG',mode='RGBA',derivedFrom=[srcinfo(p)],operation=dict(type='official_tread_animation_generator',sampleRect=[x,y,1,h],frame=i,treadFrames=18,treadPullOffset=spec['pull'],formula='idx=y+i; if idx>=height: idx=(idx-height+pullOffset)%height'),sourceCode=dict(file='full-game/items-fx/references/Generators.java',sha256=sha(R/'full-game/items-fx/references/Generators.java'),lines=[616,640]),actualModel=None,actualQuality=None,unverifiedReason='Official procedural shifting of new painted belt pixels, not AI frame generation.',engineNotVerified=True));generated.append(dict(id=f'{unit}-treads{n}-{i}',targetAtlasRegion=f'{unit}-treads{n}-{i}',file=rel(dst),sha256=sha(dst),generationRecord=rel(dst)+'.generation.json',integrationTarget='build-generated main atlas region',sourceTreePath=None,copyIntoSourceTree=False,disposition='official_build_generator_output',generatorInput=rel(p),size=[1,h],runtimeFrame='int(unit.treadTime()) % 18',sourceDefinedDrawWidth=rect[2]/4,sourceRect=rect,mirrorByRuntime=True,engineNotVerified=True))
 return dict(file=rel(p),sha256=sha(p),generationRecord=rel(p)+'.generation.json',size=size,engineAnchorPx=[size[0]/2,size[1]/2],nativeFile=rel(src),nativeGenerationRecord=record_path(src),role='paired_treads',registration=op),generated
def main():
 if (B/'freeze-receipt.json').exists():
  raise SystemExit('This production batch is frozen. Use full-game/audit_units.py for read-only validation; rebuild requires reviewing the saved initial-input-audit and restoring permitted inputs explicitly.')
 audit=rd(B/'audit.json');rows=references(audit);parts=ingest_parts();anchors,consumers,composites=known_data();mapping={a['region']:a['mapping'] for a in audit['assets'] if a['mapping'] and not a['region'].endswith(('-cell','-heat','-glow'))};overrides=alias_map(parts,mapping,composites);mapping.update(overrides);mapping['collaris-joint-base']=dict(file=parts['joint-socket'],role='joint_base',manifest='full-game/units/manifest.json',selectionReason='Complete newly painted socket replaces former generic whole-leg alias.');exported={};generatedTreads=[]
 for region,mp in mapping.items():
  if '/weapons/' in rows[region]['sourcePath'] and 'missile' not in region and not region.endswith(('-blade','-sides','-sinks','-fin','-preview')):mp['role']='weapon'
  if mp['role']=='unknown':mp['role']='region_part'
 for region,row in rows.items():
  if region.endswith('-treads'):exported[region],frames=treads(row);generatedTreads.extend(frames)
  elif region in mapping:exported[region]=export_region(region,row,mapping[region],anchors)
 extras=[]
 for base in ['corvus-weapon','vela-weapon']:
  heat=rows[base+'-heat'];size=heat['sourceDimensions'];mr=dict(file='units/serpulo-ground-naval/parts/mech-continuous-laser.png',role='weapon',manifest='units/serpulo-ground-naval/manifest.json',selectionReason='Named source weapon has a heat image but no standalone source-tree base PNG. The redesigned body-only art requires the already-authored independent laser module.');extraRow=dict(sourcePath='additional-atlas/'+base+'.png',sourceDimensions=size,sourceAlphaBounds=[0,0,*size],sourceGitBlob=None,sourceSha256=None);exported[base]=export_region(base,extraRow,mr,anchors);extras.append(dict(id=base,**exported[base],targetAtlasRegion=base,integrationTarget='core/assets-raw/sprites/units/weapons/'+base+'.png',sourceTreePath='core/assets-raw/sprites/units/weapons/'+base+'.png',copyIntoSourceTree=True,disposition='additional_complete_weapon_base_for_redesigned_body',reason=mr['selectionReason'],sourcePNGPresent=False,sizeEvidence='matching official '+base+'-heat canvas',engineNotVerified=True))
 for region,row in rows.items():
  if region not in exported:
   assert region.endswith(('-cell','-heat','-glow')),(region,'unmapped nonmask');exported[region]=mask_export(region,row,exported,rows)
 entries=[]
 for region,row in rows.items():
  en=exported[region];entries.append(dict(id=region,region=region,sourcePath=row['sourcePath'],sourceGitBlob=row['sourceGitBlob'],sourceDimensions=row['sourceDimensions'],sourceSha256=row['sourceSha256'],**en,engineFile=en['file'],engineSha256=en['sha256'],nativeSha256=sha(R/en['nativeFile']),consumers=consumers.get(region,[]),status='exported_pending_final_qa',engineNotVerified=True))
 conflicts={k:dict(selected=mapping[k],otherCandidates=v,consumers=consumers.get(k,[]),policy='One canonical atlas output per shared region. All consumers use selected image; no frozen file modified.') for k,v in audit['mappingConflicts'].items()}
 wr(B/'manifest.json',dict(schemaVersion=2,commit='17012d61d9e4c3cbd9820d87e81c24495486ac53',status='all_290_exported_pending_qa',assetCount=len(entries),assets=entries,additionalAtlasRegions=extras,generatedAtlasRegions=generatedTreads,sourceMappingCount=len(mapping),derivedMaskCount=sum(a['role'].endswith('_mask') for a in entries),mappingConflictsResolved=conflicts,additionalPaintedComponents=parts,engineNotVerified=True,coordinatePolicy='Original region canvas sizes and draw centers retained. Limb textures registered to engine U axis; weapon pivots use declared native art anchors where supplied. Actual game motion is not yet tested.'))
 print(json.dumps({'exported':len(entries),'maskCount':sum(a['role'].endswith('_mask') for a in entries),'fallbackMasks':[a['id'] for a in entries if a.get('maskFallback')]}))
if __name__=='__main__':main()
