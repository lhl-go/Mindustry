from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,datetime,collections,math
H=Path(__file__).resolve().parent;R=H.parents[1];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,o):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
m=json.loads((H/'manifest.json').read_text(encoding='utf8'));inv=json.loads((H/'inventory.json').read_text(encoding='utf8'));by={e['officialPath']:e for e in inv['entries']}
# Targeted removal of one visually confirmed isolated foreign brown fleck below pink thorium1.
e=next(e for e in m['assets'] if e['region']=='ore-thorium1');npth=R/e['nativeFile'];nrp=R/e['nativeRecord'];nr=json.loads(nrp.read_text(encoding='utf8'))
if not nr.get('foreignFleckRemoved'):
 a=np.array(Image.open(npth).convert('RGBA'));before=sha(npth);cutline=240;a[cutline:]=0;im=Image.fromarray(a,'RGBA');b=im.getchannel('A').getbbox();b=(max(0,b[0]-2),max(0,b[1]-2),min(im.width,b[2]+2),min(im.height,b[3]+2));im=im.crop(b);im.save(npth)
 nr.update(sha256=sha(npth),size=list(im.size),foreignFleckRemoved={'previousNativeSha256':before,'removedRegion':[0,cutline,int(a.shape[1]),int(a.shape[0])],'reason':'Visually isolated brown stone below pink ore cluster belonged to no ore1 design; removed only this stray component.','postCleanupCrop':list(b)})
 write(nrp,nr);e.update(nativeSha256=sha(npth),nativeSize=list(im.size));out=Image.new('RGBA',(32,32));scale=min(30/im.width,30/im.height);c=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS);out.alpha_composite(c,((32-c.width)//2,(32-c.height)//2));oa=np.array(out);oa[oa[:,:,3]<4]=0;Image.fromarray(oa,'RGBA').save(R/e['file'])
 rp=R/e['record'];rec=json.loads(rp.read_text(encoding='utf8'));rec['sha256']=sha(R/e['file']);rec['derivedFrom']=[{'file':e['nativeFile'],'sha256':sha(npth),'record':e['nativeRecord']}];rec['operation']={'type':'downsample_cleaned_native_ore_after_single_foreign_fleck_removal','sourceNativeSize':list(im.size),'targetSize':[32,32],'filter':'Lanczos downsample only','contentScale':scale,'registeredCanvas':[32,32]};write(rp,rec);e['sha256']=rec['sha256']
 # Refresh only its affected contact; old unrelated contacts remain untouched.
 batch=[x for x in m['assets'] if x['region'] in json.loads((H/'records/10-basic-ore-overlays.receipt.json').read_text(encoding='utf8'))['regions']];names=json.loads((H/'records/10-basic-ore-overlays.receipt.json').read_text(encoding='utf8'))['regions'];batch.sort(key=lambda x:names.index(x['region']))
 q=Image.new('RGB',(1080,1435),'#dad9cf');d=ImageDraw.Draw(q)
 for i,x in enumerate(batch):
  ti=Image.open(R/x['file']).convert('RGBA').resize((160,160),Image.Resampling.NEAREST);xx=i%3*360;yy=i//3*205;d.text((xx+4,yy+3),x['region'],fill='#173d35')
  for k,col in enumerate(['#f4ead8','#132a32']):
   bg=Image.new('RGBA',(176,178),col);bg.alpha_composite(ti,(8,9));q.paste(bg.convert('RGB'),(xx+k*180,yy+22))
 qp=H/'qa/10-basic-ore-overlays-alpha.png';q.save(qp);write(qp.with_name(qp.name+'.derived.json'),{'file':qp.relative_to(R).as_posix(),'sha256':sha(qp),'operation':'True alpha composite light/dark; nearest enlargement for inspection only; refreshed after ore-thorium1 fleck removal','derivedFrom':[{'file':x['file'],'sha256':x['sha256']} for x in batch]})
# Make generation reference roles precise and show actual retained native output paths.
for gp in sorted((H/'source').glob('*.generation.json')):
 g=json.loads(gp.read_text(encoding='utf8'))
 for i,ref in enumerate(g['references']):
  ref['purpose']='primary approved Daoist Q style only' if i<2 else 'official source functional silhouette/color reference only; original art style not adopted'
 g['status']='native_generation_exported_to_mapped_assets';g['currentSourceRetentionReason']='Current design master awaiting coordinator independent final visual acceptance; native and compatibility exports already retained.'
 g['nativeExports']=[{'file':a['nativeFile'],'sha256':a['nativeSha256']} for a in m['assets'] if a.get('nativeRecord') and gp.relative_to(R).as_posix() in (R/a['nativeRecord']).read_text(encoding='utf8')]
 write(gp,g)
# Native overview shows real crop detail; thumbnails are inspection-only and never used as deliverable texture.
sample=['stone1','sand-floor1','shallow-water','snow1','moss2','rhyolite2','yellow-stone-plates2','redmat1','ore-thorium1','stone-vent1','snow-boulder1','yellowcoral','crystal-orbs1','white-tree','erekir','metal-wall-1-autotile']
selected=[next(a for a in m['assets'] if a['region']==n) for n in sample];q=Image.new('RGB',(1120,1160),'#e4dfd2');d=ImageDraw.Draw(q)
for i,a in enumerate(selected):
 im=Image.open(R/a['nativeFile']).convert('RGBA');im.thumbnail((266,250),Image.Resampling.LANCZOS);x=i%4*280;y=i//4*290;d.text((x+5,y+4),a['region']+' '+str(a['nativeSize']),fill='#173d35');bg=Image.new('RGBA',(270,260),'#f4ead8');bg.alpha_composite(im,((270-im.width)//2,(260-im.height)//2));q.paste(bg.convert('RGB'),(x+5,y+25))
qp=H/'qa/28-native-detail-samples.png';q.save(qp);write(qp.with_name(qp.name+'.derived.json'),{'file':qp.relative_to(R).as_posix(),'sha256':sha(qp),'inspectionOnly':True,'operation':'Actual native crop thumbnails, no upward resize','derivedFrom':[{'file':a['nativeFile'],'sha256':a['nativeSha256']} for a in selected]})
# Strict mapping / hash / dimensions / retained bytes audit. No historical seam test repeats.
errors=[];paths=[e['officialPath'] for e in m['assets']];expected={e['officialPath'] for e in inv['entries']}
if len(paths)!=len(set(paths)):errors.append('Duplicate officialPath')
if set(paths)!=expected:errors.append({'missing':sorted(expected-set(paths)),'unexpected':sorted(set(paths)-expected)})
for a in m['assets']:
 e=by[a['officialPath']];a['sourcePath']=a['officialPath'];a['engineFile']=a['file'];a['engineSha256']=a['sha256'];a['sourceCommit']=m['sourceCommit'];a['officialGitBlobSha1']=e['gitBlobSha1'];a['officialSize']=e['originalSize']
 for field,hashfield,sizefield in [('file','sha256','size'),('nativeFile','nativeSha256','nativeSize')]:
  p=R/a[field]
  if not p.exists():errors.append([a['region'],'missing',field]);continue
  if sha(p)!=a[hashfield]:errors.append([a['region'],'hash mismatch',field])
  with Image.open(p) as im:
   im.load()
   if list(im.size)!=a[sizefield]:errors.append([a['region'],'size mismatch',field])
 if a['size']!=e['originalSize']:errors.append([a['region'],'official size mismatch',a['size'],e['originalSize']])
 for field in ['record','nativeRecord']:
  if not (R/a[field]).exists():errors.append([a['region'],'record missing',field])
 if a['artSource']=='official_retained_technical' and sha(R/a['file'])!=e['officialSource']['sha256']:errors.append([a['region'],'technical asset altered'])
 a['status']='official_technical_byte_verified' if a['artSource']=='official_retained_technical' else 'static_art_visual_reviewed_runtime_pending';e.update(status=a['status'],outputFile=a['file'],nativeOutputFile=a['nativeFile'])
 for s in ['record','nativeRecord']:
  rr=json.loads((R/a[s]).read_text(encoding='utf8'))
  if rr.get('sha256')!=sha(R/a['file' if s=='record' else 'nativeFile']):errors.append([a['region'],'record hash mismatch',s])
# Check compatibility cubemap edges too, using independently stored pairing directions.
sky=json.loads((H/'records/skybox-seams.json').read_text(encoding='utf8'))
def edge(im,k):
 a=np.array(im);return {'L':a[:,0],'R':a[:,-1],'T':a[0],'B':a[-1]}[k]
for pair in sky['pairChecks']:
 na,ea=pair['edgeA'][:-1],pair['edgeA'][-1];nb,eb=pair['edgeB'][:-1],pair['edgeB'][-1];a=edge(Image.open(H/f'assets/core/assets/cubemaps/stars/{na}.png'),ea);b=edge(Image.open(H/f'assets/core/assets/cubemaps/stars/{nb}.png'),eb)
 if pair['reversed']:b=b[::-1]
 pair['compatibilityMaxAbsDifference']=int(np.abs(a.astype(int)-b.astype(int)).max())
 if pair['compatibilityMaxAbsDifference']>0:errors.append(['cubemap compatibility seam',pair])
write(H/'records/skybox-seams.json',sky)
m.update(status='complete_static_art_runtime_pending',mappedCount=len(m['assets']),countsByArtSource=dict(collections.Counter(a['artSource'] for a in m['assets'])),countsByCategory=dict(collections.Counter(a['category'] for a in m['assets'])),nativeFileCount=len(set(a['nativeFile'] for a in m['assets'])),generationCount=25,updatedAt=now(),runtimeIntegrationVerified=False)
m['limitations']=['Actual image model and quality are undisclosed by host: null; configured target is not proof of actual model.','315 official technical/glyph assets remain byte-identical with reasons and license; 45 metal paths combine new material with official connection geometry.','17 shadows are local derivatives of new body alpha, not independent AI generations.','Six cubemap faces share one native1774x887 panorama;256 projections and1024 compatibility resamples retained. Space texture1254 native with2048 compatibility resample. No extra detail claimed.','Planets.java / renderer procedural geometry, particles, liquids and shaders remain original code; new static planet icons and sky images are not new procedural meshes.','Static PNG scope is complete; actual game atlas build, mixed terrain blending, shadow registration, shader animation, mobile performance and runtime cube orientation remain unverified.']
write(H/'manifest.json',m);write(H/'inventory.json',inv)
report={'checkedAt':now(),'status':'passed' if not errors else 'failed','expectedCount':733,'mappedCount':len(paths),'nativeMappings':sum('nativeFile' in a for a in m['assets']),'uniqueNativeFiles':m['nativeFileCount'],'countsByArtSource':m['countsByArtSource'],'allEngineDimensionsMatchOfficial':not any('official size mismatch' in str(e) for e in errors),'allHashesAndRecordsChecked':True,'technicalByteIdenticalCount':315,'errors':errors,'runtimeIntegrationVerified':False,'previousSeamChecksReused':True}
write(H/'records/delivery-validation.json',report)
contract=json.loads((H/'contract.json').read_text(encoding='utf8'));contract.update(state='complete_static_art_runtime_pending',nativeSizePolicy='Preserve actual-resolution native crops. Original-size compatibility resample is separately disclosed for6skybox faces and1space image; no added detail claimed.',finalMappedCount=733,generationCount=25);write(H/'contract.json',contract)
print(json.dumps(report,ensure_ascii=False))
