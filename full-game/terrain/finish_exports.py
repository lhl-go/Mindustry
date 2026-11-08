from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,hashlib,datetime,math
from export_native import periodic
H=Path(__file__).resolve().parent;R=H.parents[1];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
inv=json.loads((H/'inventory.json').read_text(encoding='utf8'));m=json.loads((H/'manifest.json').read_text(encoding='utf8'));by={e['region']:e for e in inv['entries']};em={e['region']:e for e in m['assets']}
def install(e,im,native,art,rec,native_role,native_path=None):
 dest=H/'assets'/e['officialPath'];dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest)
 nd=native_path or H/'native'/e['officialPath'];nd.parent.mkdir(parents=True,exist_ok=True)
 if native is not None:native.save(nd)
 ni=Image.open(nd);nr=nd.with_name(nd.name+'.derived.json')
 if not nr.exists():write(nr,{'schemaVersion':1,'file':nd.relative_to(R).as_posix(),'sha256':sha(nd),'size':list(ni.size),'mode':ni.mode,'derivedFrom':rec['derivedFrom'],'operation':rec.get('nativeOperation',rec['operation']),'actualModel':None,'actualQuality':None,'role':native_role})
 rec.update(schemaVersion=1,file=dest.relative_to(R).as_posix(),sha256=sha(dest),createdAt=now(),width=im.width,height=im.height,mode=im.mode,format='PNG',actualModel=None,actualQuality=None,modelEvidence='Inherited host generation; actual model/quality undisclosed. Local pixel operation is not a new generation.')
 write(dest.with_name(dest.name+'.derived.json'),rec)
 entry={'officialPath':e['officialPath'],'sourcePath':e['officialPath'],'region':e['region'],'file':rec['file'],'sha256':rec['sha256'],'record':rec['file']+'.derived.json','artSource':art,'category':e['category'],'size':list(im.size),'opaque':im.mode=='RGB' or im.getchannel('A').getextrema()[0]==255,'nativeFile':nd.relative_to(R).as_posix(),'nativeSha256':sha(nd),'nativeSize':list(ni.size),'nativeRecord':nr.relative_to(R).as_posix(),'nativeRole':native_role,'status':'exported_needs_visual_review','runtimeIntegrationVerified':False}
 if art.endswith('official_geometry'):entry['technicalReuseReason']='Official base connection geometry/alpha retained; shares AI-painted material with corresponding authored atlas.'
 m['assets']=[a for a in m['assets'] if a['officialPath']!=e['officialPath']]+[entry];e.update(status=entry['status'],outputFile=entry['file']);em[e['region']]=entry;return entry
# Six official base icons use the corresponding authored material; they are not new independent variants.
base_links={'metal-tiles-1':'metal-tiles-1-autotile','metal-tiles-11':'metal-tiles-11-autotile1','metal-tiles-12':'metal-tiles-12-autotile1','metal-wall-1':'metal-wall-1-autotile','metal-wall-2':'metal-wall-2-autotile','metal-wall-3':'metal-wall-3-autotile'}
bases=[]
for n,srcname in base_links.items():
 e=by[n];s=em[srcname];npth=R/s['nativeFile'];material=Image.open(npth).convert('RGB').resize((32,32),Image.Resampling.LANCZOS);oa=np.array(Image.open(H/e['officialSource']['file']).convert('RGBA'));l=oa[:,:,:3].mean(2);shade=np.ones_like(l) if l.max()==l.min() else .3+.7*(l-l.min())/(l.max()-l.min());out=Image.fromarray(np.dstack([(np.array(material)*shade[:,:,None]).astype(np.uint8),oa[:,:,3]]),'RGBA')
 rec={'kind':'hybrid_base_icon','derivedFrom':[{'file':s['nativeFile'],'sha256':s['nativeSha256'],'record':s['nativeRecord'],'role':'shared material of corresponding authored atlas'},{'file':(H/e['officialSource']['file']).relative_to(R).as_posix(),'sha256':e['officialSource']['sha256'],'officialPath':e['officialPath'],'sourceCommit':m['sourceCommit'],'role':'original base geometry/shading'}],'operation':{'type':'downsample_shared_native_material_to32_apply_official_alpha_and_normalized_shading','sharedWith':srcname,'newIndependentVariant':False},'license':'full-game/terrain/licenses/Mindustry-LICENSE.txt'}
 bases.append(install(e,out,None,'host_image_material_with_official_geometry',rec,'shared AI material swatch for base icon; not a separately painted variant',npth))
# Derive shadows from actual new painted silhouettes; renderer still owns offsets and rotations.
shadows=[]
for e in inv['entries']:
 if '/props/' not in e['officialPath'] or '-shadow' not in e['region']:continue
 n=e['region'];body=n.replace('-shadow','');b=em[body];native_body=Image.open(R/b['nativeFile']).convert('RGBA');body_engine=Image.open(R/b['file']).convert('RGBA');target=e['originalSize'];opacity=138 if n.startswith('white-tree') else (229 if n.startswith('arkyic') else 255)
 def silhouette(im,pad,blur):
  a=im.getchannel('A').point(lambda x:round(x*opacity/255));a=Image.fromarray(np.pad(np.array(a),pad)).filter(ImageFilter.GaussianBlur(blur));o=Image.new('RGBA',a.size);o.putalpha(a);return o
 # Native shadow uses a small proportional blur and padding, never a larger painted silhouette.
 pad=math.ceil(max(native_body.size)*.025);native=silhouette(native_body,pad,max(1,max(native_body.size)/200))
 # Engine footprint matches body pixel scale except a necessary shrink to original shadow canvas.
 padded=silhouette(body_engine,3,1.25);scale=min(1,(target[0]-2)/padded.width,(target[1]-2)/padded.height);size=[max(1,round(v*scale)) for v in padded.size];padded=padded.resize(size,Image.Resampling.LANCZOS);out=Image.new('RGBA',target);out.alpha_composite(padded,((target[0]-padded.width)//2,(target[1]-padded.height)//2))
 rec={'kind':'derived_shadow','derivedFrom':[{'file':b['file'],'sha256':b['sha256'],'record':b['record'],'role':'actual new body silhouette'},{'file':b['nativeFile'],'sha256':b['nativeSha256'],'record':b['nativeRecord'],'role':'native painted body alpha'}],'operation':{'type':'black_alpha_silhouette_soften_and_center_on_official_shadow_canvas','maximumAlpha':opacity,'blurSigmaEnginePixels':1.25,'engineSilhouetteScale':scale,'shadowOffset':'unchanged runtime TallBlock -3 / TreeBlock -4 world units; not baked into image','runtimeRotation':'unchanged source class','newPaintedVariant':False},'nativeOperation':{'type':'native_body_alpha_black_shadow_with_2.5_percent_padding_and_softening','maximumAlpha':opacity,'bodyNotUpscaled':True}}
 shadows.append(install(e,out,native,'derived_shadow_from_new_art',rec,'derived at native body resolution; generated silhouette, local shadow operation'))
# Space material: native 1254; explicit original-size compatibility resample, no claim of added detail.
p=H/'source/25-space-material.png';im=Image.open(p).convert('RGB');a=periodic(np.array(im));native=Image.fromarray(a,'RGB');out=native.resize((2048,2048),Image.Resampling.LANCZOS);a=np.array(out);a[0]=(a[0].astype(np.uint16)+a[-1])//2;a[-1]=a[0];a[:,0]=(a[:,0].astype(np.uint16)+a[:,-1])//2;a[:,-1]=a[:,0];out=Image.fromarray(a,'RGB');e=next(e for e in inv['entries'] if e['officialPath']=='core/assets/sprites/space.png')
space=install(e,out,native,'host_image_derived_compatibility_resample',{'kind':'derived_repeat_texture','derivedFrom':[{'file':p.relative_to(R).as_posix(),'sha256':sha(p),'generationRecord':p.relative_to(R).as_posix()+'.generation.json'}],'nativeOperation':{'type':'native periodic-plus-smooth seam cleanup','sourceSize':list(im.size),'resized':False},'operation':{'type':'periodic_native_cleanup_then_explicit_compatibility_resample','nativeSize':list(im.size),'compatibilitySize':[2048,2048],'filter':'Lanczos','upscaled':True,'newPaintedDetail':False}},'native-resolution space material after local seam cleanup; compatibility copy is resampled')
# Panorama: horizontal seam smoothing and uniform cap pixels, then OpenGL cube projection.
p=H/'source/24-star-panorama.png';orig=np.array(Image.open(p).convert('RGB')).astype(float);a=orig.copy();h,w=a.shape[:2]
for j in range(24):
 q=(24-j)/24;v=(a[:,j]+a[:,-1-j])/2;a[:,j]=(1-q)*a[:,j]+q*v;a[:,-1-j]=(1-q)*a[:,-1-j]+q*v
for side in [0,1]:
 edge=a[0 if side==0 else -1].mean(0)
 for j in range(24):
  idx=j if side==0 else -1-j;q=(24-j)/24;a[idx]=(1-q)*a[idx]+q*edge
a=np.clip(np.rint(a),0,255).astype(np.uint8);pan=Image.fromarray(a,'RGB');panpath=H/'native/stars-equirectangular.png';pan.save(panpath);panrec={'schemaVersion':1,'file':panpath.relative_to(R).as_posix(),'sha256':sha(panpath),'size':[w,h],'resized':False,'operation':'native panorama opposite longitude edges paired over24px; polar24px tapered to uniform cap; no new painted detail','derivedFrom':[{'file':p.relative_to(R).as_posix(),'sha256':sha(p),'generationRecord':p.relative_to(R).as_posix()+'.generation.json'}]};write(panpath.with_name(panpath.name+'.derived.json'),panrec)
def directions(n):
 u,v=np.meshgrid(np.linspace(-1,1,n),np.linspace(-1,1,n));o=np.ones_like(u)
 return {'right':np.stack([o,-v,-u],2),'left':np.stack([-o,-v,u],2),'top':np.stack([u,o,v],2),'bottom':np.stack([u,-o,-v],2),'front':np.stack([u,-v,o],2),'back':np.stack([-u,-v,-o],2)}
def sample(d):
 d=d/np.linalg.norm(d,axis=2,keepdims=True);x=(np.arctan2(d[:,:,2],d[:,:,0])/(2*np.pi)+.5)*(w-1);y=(.5-np.arcsin(d[:,:,1])/np.pi)*(h-1);x0=np.floor(x).astype(int);y0=np.floor(y).astype(int);x1=np.minimum(x0+1,w-1);y1=np.minimum(y0+1,h-1);wx=(x-x0)[:,:,None];wy=(y-y0)[:,:,None];out=a[y0,x0]*(1-wx)*(1-wy)+a[y0,x1]*wx*(1-wy)+a[y1,x0]*(1-wx)*wy+a[y1,x1]*wx*wy;return np.rint(out).astype(np.uint8)
# 256 faces are below panorama equatorial 443.5 pixels/90degrees; compatibility1024 is explicitly resampled.
dirs=directions(256);faces={n:sample(d) for n,d in dirs.items()};cube=[]
for name,arr in faces.items():
 e=next(e for e in inv['entries'] if e['officialPath']==f'core/assets/cubemaps/stars/{name}.png');native=Image.fromarray(arr,'RGB');out=native.resize((1024,1024),Image.Resampling.BILINEAR)
 rec={'kind':'projected_skybox_face','derivedFrom':[{'file':panrec['file'],'sha256':panrec['sha256'],'record':panrec['file']+'.derived.json'}],'nativeOperation':{'type':'equirectangular_to_OpenGL_cubemap_bilinear_sampling','panoramaSize':[w,h],'faceSize':[256,256],'equatorialSourceSamplesPer90Degrees':w/4,'side':name,'pixelGridIncludesBoundaryDirections':True},'operation':{'type':'project256_face_then_explicit_compatibility_resample1024','filter':'Bilinear preserves shared boundary rows','newPaintedDetail':False,'upscaled':True},'orientationEvidence':{'url':'https://raw.githubusercontent.com/Anuken/Arc/7445105cd2/arc-core/src/arc/graphics/Cubemap.java','axisMap':{'right':'+X','left':'-X','top':'+Y','bottom':'-Y','front':'+Z','back':'-Z'},'dependencyEvidence':'Mindustry fixed commit gradle.properties archash=7445105cd2'}}
 cube.append(install(e,out,native,'host_image_panorama_projection',rec,'256px cube projection from native1774x887 panorama; not independently generated face'))
# Independent edge pairing from matching three-dimensional boundary directions.
checks=[];edges=[]
for n,d in dirs.items():
 for edge,dd,pix in [('L',d[:,0],faces[n][:,0]),('R',d[:,-1],faces[n][:,-1]),('T',d[0],faces[n][0]),('B',d[-1],faces[n][-1])]:edges.append((n,edge,dd,pix))
used=set()
for i,(n,edge,dd,pix) in enumerate(edges):
 if i in used:continue
 for j,(nn,ee,d2,p2) in enumerate(edges):
  if i==j or n==nn or j in used:continue
  rev=False
  if np.allclose(dd,d2):pass
  elif np.allclose(dd,d2[::-1]):rev=True;p2=p2[::-1]
  else:continue
  used.update([i,j]);checks.append({'edgeA':n+edge,'edgeB':nn+ee,'reversed':rev,'nativeMaxAbsDifference':int(np.abs(pix.astype(int)-p2.astype(int)).max())});break
assert len(checks)==12 and all(c['nativeMaxAbsDifference']==0 for c in checks)
write(H/'records/skybox-seams.json',{'checkedAt':now(),'projection':'OpenGL cube axes; fixed Arc dependency side names','nativePanorama':panrec,'nativeFaces':256,'compatibilityFaces':1024,'pairChecks':checks,'panoramaLongitudeByteEqual':bool(np.array_equal(a[:,0],a[:,-1])),'topCapUniform':bool(np.all(a[0]==a[0,0])),'bottomCapUniform':bool(np.all(a[-1]==a[-1,0])),'runtimeOrientationVerified':False,'limitation':'Mathematical edge continuity passed; engine cube orientation/filtering still requires client verification.'})
# Contacts for final visual review.
def contact(items,name,cols=4):
 rows=math.ceil(len(items)/cols);q=Image.new('RGB',(cols*320,rows*210),'#e4dfd2');d=ImageDraw.Draw(q)
 for i,e in enumerate(items):
  im=Image.open(R/e['file']).convert('RGBA');im.thumbnail((148,175),Image.Resampling.LANCZOS);x=i%cols*320;y=i//cols*210;d.text((x+3,y+3),e['region'],fill='#143e35')
  for k,c in enumerate(['#f4ead8','#15313a']):
   bg=Image.new('RGBA',(156,180),c);bg.alpha_composite(im,((156-im.width)//2,(180-im.height)//2));q.paste(bg.convert('RGB'),(x+k*160,y+24))
 qp=H/'qa'/name;q.save(qp);write(qp.with_name(qp.name+'.derived.json'),{'file':qp.relative_to(R).as_posix(),'sha256':sha(qp),'operation':'Light and dark true alpha composite for visual inspection','derivedFrom':[{'file':e['file'],'sha256':e['sha256']} for e in items]})
contact(bases+shadows,'26-base-icons-shadows.png')
contact(cube+[space],'27-skybox-space.png',3)
write(H/'manifest.json',m);write(H/'inventory.json',inv);print(json.dumps({'mapped':len(m['assets']),'nativeMapped':sum('nativeFile' in e for e in m['assets']),'newBases':len(bases),'newShadows':len(shadows),'cubeFaces':len(cube),'sourceSpace':space['nativeSize']}))
