from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,datetime,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest_path=HERE/'manifest.json';m=json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {'schemaVersion':1,'status':'in_production','sourceCommit':'17012d61d9e4c3cbd9820d87e81c24495486ac53','assets':[],'runtimeIntegrationVerified':False}
inv=json.loads((HERE/'inventory.json').read_text(encoding='utf-8'));byregion={e['region']:e for e in inv['entries']}
for stem in sys.argv[1:]:
 p=HERE/'source'/(stem+'.png');receipt=json.loads((HERE/'records'/(stem+'.receipt.json')).read_text(encoding='utf-8'));im=Image.open(p).convert('RGB');regions=receipt['regions'];cols=receipt.get('grid',[3,len(regions)//3])[0];rows=(len(regions)+cols-1)//cols
 exported=[]
 for i,region in enumerate(regions):
  e=byregion[region];x=i%cols;y=i//cols;x0=round(x*im.width/cols);x1=round((x+1)*im.width/cols);y0=round(y*im.height/rows);y1=round((y+1)*im.height/rows)
  if 'rowBounds' in receipt:y0,y1=receipt['rowBounds'][y:y+2]
  if 'columnBounds' in receipt:x0,x1=receipt['columnBounds'][x:x+2]
  native=im.crop((x0+2,y0+2,x1-2,y1-2));target=e['originalSize'] or [32,32]
  if native.width<target[0] or native.height<target[1]:raise ValueError('Would upscale '+region)
  tile=native.resize(target,Image.Resampling.LANCZOS);arr=np.array(tile).astype(np.float32)
  # Remove the smooth boundary-discontinuity component (periodic-plus-smooth decomposition).
  # This is authorized seam cleanup of AI pixels, not newly painted detail or a new variant.
  seam_before=[float(np.abs(arr[:,0]-arr[:,-1]).mean()),float(np.abs(arr[0]-arr[-1]).mean())]
  h,w=arr.shape[:2];boundary=np.zeros_like(arr)
  boundary[0]+=arr[-1]-arr[0];boundary[-1]+=arr[0]-arr[-1]
  boundary[:,0]+=arr[:,-1]-arr[:,0];boundary[:,-1]+=arr[:,0]-arr[:,-1]
  denom=2*np.cos(2*np.pi*np.arange(h)/h)[:,None]+2*np.cos(2*np.pi*np.arange(w)/w)[None,:]-4
  denom[0,0]=1; spectrum=np.fft.fft2(boundary,axes=(0,1))/denom[:,:,None];spectrum[0,0]=0
  smooth=np.fft.ifft2(spectrum,axes=(0,1)).real;arr-=smooth
  strip=min(3,min(target)//8)
  for j in range(strip):
   weight=(strip-j)/strip;avg=(arr[:,j]+arr[:,-1-j])/2;arr[:,j]=arr[:,j]*(1-weight)+avg*weight;arr[:,-1-j]=arr[:,-1-j]*(1-weight)+avg*weight
  for j in range(strip):
   weight=(strip-j)/strip;avg=(arr[j]+arr[-1-j])/2;arr[j]=arr[j]*(1-weight)+avg*weight;arr[-1-j]=arr[-1-j]*(1-weight)+avg*weight
  a=np.clip(np.rint(arr),0,255).astype(np.uint8);out=Image.fromarray(a,'RGB');dest=HERE/'assets'/e['officialPath'];dest.parent.mkdir(parents=True,exist_ok=True);out.save(dest)
  rec={'schemaVersion':1,'file':dest.relative_to(ROOT).as_posix(),'sha256':sha(dest),'createdAt':now(),'kind':'derived_image','format':'PNG','mode':'RGB','width':out.width,'height':out.height,'derivedFrom':[{'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'generationRecord':p.relative_to(ROOT).as_posix()+'.generation.json'}],'operation':{'type':'crop_native_independent_material_variant_downsample_and_seam_edge_blend','sourceBBox':[x0+2,y0+2,x1-2,y1-2],'nativeExtractedSize':list(native.size),'targetSize':target,'filter':'Lanczos downsample only','seamStripPixels':strip,'seamBlend':'paired opposing edges averaged; narrow 3px linear falloff; interior generated pixels preserved','noNewPaintedDetail':True},'actualModel':None,'actualQuality':None,'modelEvidence':'Inherited source generation; local authorized cleanup only.'}
  rec['operation']['seamBlend']='Periodic-plus-smooth boundary-discontinuity correction then paired opposing edges averaged with narrow 3px linear falloff; no new detail generated.'
  rec['operation']['periodicSmoothCorrectionRms']=float(np.sqrt((smooth*smooth).mean()))
  write(dest.with_name(dest.name+'.derived.json'),rec)
  entry={'officialPath':e['officialPath'],'region':region,'file':rec['file'],'sha256':rec['sha256'],'record':rec['file']+'.derived.json','artSource':'host_image_derived','category':e['category'],'size':target,'nativeExtractedSize':list(native.size),'opaque':True,'status':'exported_needs_visual_seam_review','seamCheck':{'beforeMeanAbsRGB':seam_before,'afterMeanAbsRGB':[float(np.abs(a[:,0].astype(float)-a[:,-1]).mean()),float(np.abs(a[0].astype(float)-a[-1]).mean())],'scope':'same-variant opposite-edge pixel continuity; mixed terrain uses engine edge stencil','passed':bool(np.array_equal(a[:,0],a[:,-1]) and np.array_equal(a[0],a[-1]))},'runtimeIntegrationVerified':False}
  m['assets']=[old for old in m['assets'] if old['officialPath']!=entry['officialPath']]+[entry];exported.append(entry)
  e['status']=entry['status'];e['outputFile']=entry['file']
 # Native 32px tiles repeated into 3x3 patches, nearest-neighbor enlarged only for QA display.
 qa=Image.new('RGB',(cols*288,rows*310),'#eee8d9');draw=ImageDraw.Draw(qa)
 for i,e in enumerate(exported):
  tile=Image.open(ROOT/e['file']).convert('RGB');patch=Image.new('RGB',(tile.width*3,tile.height*3))
  for yy in range(3):
   for xx in range(3):patch.paste(tile,(xx*tile.width,yy*tile.height))
  patch.thumbnail((270,270),Image.Resampling.NEAREST)
  if patch.width<270:patch=patch.resize((270,270),Image.Resampling.NEAREST)
  xx=(i%cols)*288;yy=(i//cols)*310;draw.text((xx+6,yy+5),e['region'],fill='#173d35');qa.paste(patch,(xx+6,yy+27))
 qp=HERE/'qa'/(stem+'-seams.png');qp.parent.mkdir(exist_ok=True);qa.save(qp)
 write(qp.with_name(qp.name+'.derived.json'),{'file':qp.relative_to(ROOT).as_posix(),'sha256':sha(qp),'operation':'3x3 repetition of exported tile, nearest-neighbor enlargement only for QA (not native art)','derivedFrom':[{'file':e['file'],'sha256':e['sha256']} for e in exported],'inspectionOnly':True})
 print(json.dumps({'batch':stem,'count':len(exported),'seamPixelContinuityPassed':all(e['seamCheck']['passed'] for e in exported),'qa':qp.relative_to(ROOT).as_posix()},ensure_ascii=False))
m['updatedAt']=now();m['mappedCount']=len(m['assets']);write(manifest_path,m);write(HERE/'inventory.json',inv)
