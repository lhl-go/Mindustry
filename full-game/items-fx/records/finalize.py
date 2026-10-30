from build import *
from PIL import ImageFilter
import base64,io
NOW=lambda:datetime.now(timezone.utc).isoformat()
INV=json.loads((BASE/'inventory.json').read_text(encoding='utf-8'))
BYID={a['id']:{k:v for k,v in a.items() if k!='status'} for a in INV['assets']}
CUSTOM={
 '09-rubble-small':[[0,0,490,455],[490,0,965,455],[965,0,1536,475],[0,475,550,1024],[550,475,1536,1024]],
 '10-rubble-large':[[0,0,430,480],[430,0,980,480],[980,0,1536,480],[0,480,730,1024],[730,480,1536,1024]],
 '12-guidance':[[0,0,550,550],[550,0,970,500],[970,0,1536,500],[0,550,560,1024],[560,500,1000,1024],[1000,500,1536,1024]],
 '11-projectiles':[[0,0,418,418],[418,0,836,418],[836,0,1254,418],[0,418,418,800],[418,418,836,800],[836,418,1254,800],[0,800,418,1254],[418,800,836,1254],[836,800,1254,1254]]}
def rel(p):return p.relative_to(ROOT).as_posix()
def srcinfo(p):return dict(file=rel(p),sha256=sha(p),generationRecord=rel(p)+'.generation.json')
def dimrecords():
 out={}
 for fp in (BASE/'records').glob('*.fetch.json'):
  j=json.loads(fp.read_text(encoding='utf-8'))
  if 'content' not in j:continue
  b=base64.b64decode(j['content']);im=Image.open(io.BytesIO(b));blob=hashlib.sha1(('blob '+str(len(b))+'\0').encode()+b).hexdigest();id=j['id']
  assert blob==BYID[id]['officialGitBlob'],(id,blob)
  out[id]=dict(size=list(im.size),mode=im.mode,sha256=hashlib.sha256(b).hexdigest(),gitBlobSha1=blob,officialPath=BYID[id]['officialPath'],retrievedVia='github_fetch_file pinned commit',sourceUrl=j['display_url'],fetchRecord=rel(fp))
 write(BASE/'records/official-dimensions.json',dict(commit=INV['commit'],count=len(out),assets=out));return out
def write_asset(id,im,rec,assets,kind='generated_art'):
 p=BASE/'assets'/f'{id}.png';p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
 rec.update(file=rel(p),sha256=sha(p),width=im.width,height=im.height,format='PNG',mode=im.mode,exportedAt=NOW())
 write(p.with_name(p.name+'.generation.json'),rec)
 assets[id]=dict(**BYID[id],file=rel(p),sha256=sha(p),size=list(im.size),generationRecord=rel(p)+'.generation.json',artKind=kind,anchorNormalized=[.5,.5],engineNotVerified=True,status='exported_pending_visual_qa')
def native(assets):
 for rp in sorted((BASE/'records').glob('*.receipt.json')):
  j=json.loads(rp.read_text(encoding='utf-8'));stem=j['stem'];src=BASE/'source'/f'{stem}.png'
  if not src.exists():continue
  im=Image.open(src).convert('RGBA');cols=j.get('cols',4);rows=j.get('rows',2)
  if len(j['names'])==6 and 'cols' not in j:cols=3
  for i,id in enumerate(j['names']):
   box=CUSTOM[stem][i] if stem in CUSTOM else [round((i%cols)*im.width/cols),round((i//cols)*im.height/rows),round((i%cols+1)*im.width/cols),round((i//cols+1)*im.height/rows)]
   if stem=='14-fire-20-39':
    bands=[0,280,560,830,1121];box[1]=bands[i//5];box[3]=bands[i//5+1]
   a=np.array(im.crop(box));alpha=a[:,:,3];alpha[alpha<16]=0;alpha[alpha>=245]=255;a[alpha==0,:3]=0
   rec=dict(derivedFrom=[srcinfo(src)],upsampled=False,actualModel=None,actualQuality=None,unverifiedReason='Source host model/quality not disclosed; see source generation record.',operation=dict(type='native_cell_crop_alpha_cleanup',crop=box,alphaBelow16ToZero=True,alphaAtLeast245To255=True,transparentRgbZeroed=True))
   cut=Image.fromarray(a);b=cut.getbbox()
   if not b:raise ValueError('empty '+id)
   if id.startswith('fire'):
    # Keep the connected flame body; isolated colored export noise and tiny detached sparks are removed.
    mask=Image.fromarray((alpha>=16).astype('uint8')).copy();coords=np.argwhere(alpha>=128);cy,cx=np.array(alpha.shape)*[.65,.5];seed=coords[np.argmin((coords[:,0]-cy)**2+(coords[:,1]-cx)**2)];ImageDraw.floodfill(mask,(int(seed[1]),int(seed[0])),2)
    keep=np.asarray(mask)==2;a[~keep]=0;cut=Image.fromarray(a);b=cut.getbbox();core=Image.fromarray((a[:,:,3]>=128).astype('uint8')*255).getbbox();anchor=[(core[0]+core[2])/2,core[3]]
    # A common fixed canvas preserves pixel scale; only translate the native extraction.
    out=Image.new('RGBA',(384,384));offset=[round(192-anchor[0]),round(330-anchor[1])];out.alpha_composite(cut,tuple(offset));rec['operation'].update(type='native_frame_extract_cleanup_register',registration='translation only; opaque-body bottom-center registered to (192,330)',translation=offset,sourceBodyBBox=list(b),canvas=[384,384],removedDetachedComponents=True)
   else:
    cut=cut.crop(b);out=Image.new('RGBA',(cut.width+32,cut.height+32));out.alpha_composite(cut,(16,16));rec['operation'].update(trim=list(b),padding=16)
   if id=='transfer-arrow':out=out.transpose(Image.Transpose.ROTATE_90);rec['operation']['orientationCorrection']='lossless 90deg CCW to match official launch-arrow/transfer-arrow shared north orientation'
   write_asset(id,out,rec,assets)
def backs(assets):
 for id in ['bullet','circle-bullet','large-bomb','large-orb','mine-bullet','missile','missile-large','shell']:
  p=ROOT/assets[id]['file'];im=Image.open(p).convert('RGBA');a=im.getchannel('A').filter(ImageFilter.MaxFilter(9));out=Image.new('RGBA',im.size,(255,255,255,0));out.putalpha(a)
  rec=dict(derivedFrom=[srcinfo(p)],operation=dict(type='projectile_back_mask_from_front_alpha',alphaDilationKernel=9,color='white for engine backColor multiplication',canvas='identical to front; center aligned'),upsampled=False,actualModel=None,actualQuality=None,unverifiedReason='Pixel-derived from AI art, no new model call.')
  write_asset(id+'-back',out,rec,assets,'derived_projectile_back_mask')
  assets[id]['layers']=[dict(file=assets[id+'-back']['file'],role='back',colorParameter='BasicBulletType.backColor'),dict(file=assets[id]['file'],role='front',colorParameter='BasicBulletType.frontColor')]
def reuse(assets):
 for fp in sorted((BASE/'records').glob('official-*.fetch.json')):
  j=json.loads(fp.read_text(encoding='utf-8'));id=j['id'];p=BASE/'assets'/f'{id}.png';b=base64.b64decode(j['content']);p.write_bytes(b);im=Image.open(p)
  rec=dict(file=rel(p),sha256=sha(p),width=im.width,height=im.height,mode=im.mode,format='PNG',artSource='exact_official_technical_texture_reuse',operation='byte-identical retained renderer mask/UV region; no generation, recoloring or resizing',officialSource=dict(repository='Anuken/Mindustry',commit=INV['commit'],path=BYID[id]['officialPath'],gitBlobSha1=j['sha'],url=j['display_url']),evidence=rel(fp),actualModel=None,actualQuality=None,unverifiedReason='Not AI-generated: exact official technical renderer texture.',sourceImageRetained=True)
  write(p.with_name(p.name+'.generation.json'),rec);assets[id]=dict(**BYID[id],file=rel(p),sha256=sha(p),size=list(im.size),generationRecord=rel(p)+'.generation.json',artKind='exact_official_technical_texture_reuse',anchorNormalized=[.5,.5],engineNotVerified=True,status='source_hash_verified')
def engine(assets,dims):
 for id,a in assets.items():
  if id not in dims:a['integrationStatus']='missing_official_dimension';continue
  size=dims[id]['size'];p=ROOT/a['file'];im=Image.open(p).convert('RGBA');dst=BASE/'engine/sprites'/a['group']/f'{id}.png';dst.parent.mkdir(parents=True,exist_ok=True)
  if a['artKind']=='exact_official_technical_texture_reuse':a.update(engineFile=a['file'],officialSize=size,engineSha256=a['sha256']);continue
  if id.startswith('fire'):
   out=im.resize(tuple(size),Image.Resampling.LANCZOS)
  else:
   # Fit the visible art in its official canvas; preserve aspect ratio and centered anchor.
   bb=im.getbbox();trim=im.crop(bb);limit=(max(1,size[0]-2),max(1,size[1]-2));trim.thumbnail(limit,Image.Resampling.LANCZOS);out=Image.new('RGBA',tuple(size));out.alpha_composite(trim,((size[0]-trim.width)//2,(size[1]-trim.height)//2))
  out.save(dst);record=dict(file=rel(dst),sha256=sha(dst),width=out.width,height=out.height,mode='RGBA',format='PNG',derivedFrom=[srcinfo(p)],operation=dict(type='downsample_for_original_engine_region_canvas',officialSize=size,resampler='Lanczos',aspectRatioPreserved=True,anchorNormalized=[.5,.5]),upsampled=False,actualModel=None,actualQuality=None,unverifiedReason='Engine export from traced native art, no new image generation.')
  write(dst.with_name(dst.name+'.generation.json'),record);a.update(engineFile=rel(dst),engineSha256=sha(dst),engineGenerationRecord=rel(dst)+'.generation.json',officialSize=size,integrationStatus='original_region_size_exported_engine_not_run')
def contact(assets,ids,name,bg):
 cols=8;tw=170;th=196;sheet=Image.new('RGB',(cols*tw,((len(ids)+cols-1)//cols)*th),bg);d=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',11)
 for i,id in enumerate(ids):
  im=Image.open(ROOT/assets[id]['file']).convert('RGBA');im.thumbnail((158,158));tile=Image.new('RGBA',(158,158),(*bg,255));tile.alpha_composite(im,((158-im.width)//2,(158-im.height)//2));x=i%cols*tw;y=i//cols*th;sheet.paste(tile.convert('RGB'),(x+6,y+6));d.text((x+6,y+167),id,font=font,fill=(215,215,205) if sum(bg)<300 else (20,50,40))
 p=BASE/'qa'/f'{name}.png';p.parent.mkdir(exist_ok=True);sheet.save(p);write(p.with_name(p.name+'.generation.json'),dict(file=rel(p),sha256=sha(p),operation='downsampled actual RGBA QA composite',derivedFrom=[srcinfo(ROOT/assets[id]['file']) for id in ids]));return rel(p)
def animation(assets):
 frames=[Image.open(ROOT/assets['fire'+str(i)]['file']).convert('RGBA') for i in range(40)]
 # APNG is a native transparent review clip, not a separate art source.
 p=BASE/'fire-loop.apng';frames[0].save(p,format='PNG',save_all=True,append_images=frames[1:],duration=37.5,loop=0,disposal=0,blend=0)
 write(p.with_name(p.name+'.generation.json'),dict(file=rel(p),sha256=sha(p),operation='pack 40 registered frames into APNG review animation',frameCount=40,durationMsPerFrame=37.5,derivedFrom=[srcinfo(ROOT/assets['fire'+str(i)]['file']) for i in range(40)]))
 write(BASE/'fire.animation.json',dict(commit=INV['commit'],officialClass='mindustry.entities.comp.FireComp',source='full-game/items-fx/references/FireComp.java',sourceSha256=sha(BASE/'references/FireComp.java'),sourceParameters=dict(frames=40,durationTicks=90,ticksPerFrame=2.25,warmupDurationTicks=20),fps=60/2.25,durationMs=1500,loop=True,canvas=[384,384],atlasAnchorNormalized=[.5,.5],visualBaseNormalized=[.5,330/384],runtimeFrame='floor(animation), animation += Time.delta / (duration / frames); animation %= frames',runtimeLight='Drawf.light radius=50+Mathf.absin(5,5), Pal.lightFlame, opacity0.6; retain original.',frames=[dict(index=i,id='fire'+str(i),file=assets['fire'+str(i)]['file'],engineFile=assets['fire'+str(i)].get('engineFile'),durationTicks=2.25,durationMs=37.5,anchorNormalized=[.5,.5]) for i in range(40)],engineNotVerified=True))
def main():
 dims=dimrecords();assets={};native(assets);backs(assets);reuse(assets);engine(assets,dims);animation(assets)
 artids=[id for id in assets if not id.startswith('fire') and assets[id]['artKind']!='exact_official_technical_texture_reuse'];fireids=['fire'+str(i) for i in range(40)];techids=[id for id in assets if assets[id]['artKind']=='exact_official_technical_texture_reuse'];contacts=[]
 for name,ids in [('art',artids),('fire',fireids),('technical',techids)]:
  for label,bg in [('light',(245,240,222)),('dark',(28,39,38))]:contacts.append(contact(assets,ids,name+'-'+label,bg))
 missing=sorted(set(BYID)-set(assets));write(BASE/'manifest.json',dict(status='all_assets_exported_pending_final_review',commit=INV['commit'],sourcePathCount=len(BYID),assetCount=len(assets),missing=missing,assets=list(assets.values()),contacts=contacts,engineNotVerified=True));print(json.dumps({'assets':len(assets),'dimensions':len(dims),'missing':missing,'contacts':contacts}))
if __name__=='__main__':main()
