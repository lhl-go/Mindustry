from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,datetime,sys
H=Path(__file__).resolve().parent;R=H.parents[1];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def periodic(a):
 a=a.astype(float);h,w=a.shape[:2];v=np.zeros_like(a);v[0]+=a[-1]-a[0];v[-1]+=a[0]-a[-1];v[:,0]+=a[:,-1]-a[:,0];v[:,-1]+=a[:,0]-a[:,-1]
 d=2*np.cos(2*np.pi*np.arange(h)/h)[:,None]+2*np.cos(2*np.pi*np.arange(w)/w)[None,:]-4;d[0,0]=1;s=np.fft.fft2(v,axes=(0,1))/d[:,:,None];s[0,0]=0;a-=np.fft.ifft2(s,axes=(0,1)).real
 for j in range(3):
  q=(3-j)/3;v=(a[:,j]+a[:,-1-j])/2;a[:,j]=(1-q)*a[:,j]+q*v;a[:,-1-j]=(1-q)*a[:,-1-j]+q*v
 for j in range(3):
  q=(3-j)/3;v=(a[j]+a[-1-j])/2;a[j]=(1-q)*a[j]+q*v;a[-1-j]=(1-q)*a[-1-j]+q*v
 return np.clip(a,0,255)
inv=json.loads((H/'inventory.json').read_text(encoding='utf-8'));by={e['region']:e for e in inv['entries']};mp=H/'manifest.json';m=json.loads(mp.read_text(encoding='utf-8'))
for stem in sys.argv[1:]:
 p=H/'source'/(stem+'.png');rec=json.loads((H/'records'/(stem+'.receipt.json')).read_text(encoding='utf-8'));im=Image.open(p).convert('RGB');cols,rows=rec['grid'];exports=[]
 for i,n in enumerate(rec['regions']):
  e=by[n];x=i%cols;y=i//cols;box=[round(x*im.width/cols)+2,round(y*im.height/rows)+2,round((x+1)*im.width/cols)-2,round((y+1)*im.height/rows)-2];native=im.crop(box);src=H/e['officialSource']['file'];official=Image.open(src).convert('RGBA');oa=np.array(official);tile=periodic(np.array(native.resize((32,32),Image.Resampling.LANCZOS)))
  material=np.tile(tile,(int(np.ceil(official.height/32)),int(np.ceil(official.width/32)),1))[:official.height,:official.width]
  lum=oa[:,:,:3].astype(float).mean(2);lo,hi=float(lum.min()),float(lum.max());shade=np.ones_like(lum) if hi==lo else .30+.70*(lum-lo)/(hi-lo)
  out=np.dstack([np.clip(material*shade[:,:,None],0,255).astype(np.uint8),oa[:,:,3]]);dest=H/'assets'/e['officialPath'];dest.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(out,'RGBA').save(dest)
  r={'schemaVersion':1,'file':dest.relative_to(R).as_posix(),'sha256':sha(dest),'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'kind':'hybrid_texture_composite','width':official.width,'height':official.height,'mode':'RGBA','format':'PNG','derivedFrom':[{'file':p.relative_to(R).as_posix(),'sha256':sha(p),'generationRecord':p.relative_to(R).as_posix()+'.generation.json','role':'new AI-painted material'},{'file':src.relative_to(R).as_posix(),'sha256':sha(src),'officialPath':e['officialPath'],'sourceCommit':'17012d61d9e4c3cbd9820d87e81c24495486ac53','role':'exact existing connection geometry, alpha and normalized structural shading'}],'operation':{'type':'crop_native_material_downsample_periodic32_then_apply_official_connection_shading','sourceBBox':box,'nativeExtractedSize':list(native.size),'materialTileSize':[32,32],'geometryUnchanged':True,'officialAlphaByteUnchanged':True,'geometryShadingRange':[.30,1.0],'note':'Each path has its own independently painted native swatch. Repetition inside a single128x128 logical atlas is one material skin, not claimed as sixteen new variants.'},'artSource':'host_image_material_with_official_geometry','license':{'file':'full-game/terrain/licenses/Mindustry-LICENSE.txt','reason':'Official connection shape/shading remains derived upstream GPL repository asset; new material source explicitly separate.'},'actualModel':None,'actualQuality':None,'modelEvidence':'AI material source actual model/quality undisclosed; official geometry is not AI generated.'}
  write(dest.with_name(dest.name+'.derived.json'),r)
  entry={'officialPath':e['officialPath'],'region':n,'file':r['file'],'sha256':r['sha256'],'record':r['file']+'.derived.json','artSource':r['artSource'],'category':e['category'],'size':list(official.size),'nativeExtractedSize':list(native.size),'opaque':bool(oa[:,:,3].min()==255),'status':'exported_needs_visual_autotile_review','runtimeIntegrationVerified':False,'technicalReuseReason':'Exact original logical connection silhouette and structural shading retained; independently AI-painted material applied.'}
  m['assets']=[a for a in m['assets'] if a['officialPath']!=e['officialPath']]+[entry];e['status']=entry['status'];e['outputFile']=entry['file'];exports.append(entry)
 qa=Image.new('RGB',(cols*250,rows*275),'#eee8d9');d=ImageDraw.Draw(qa)
 for i,e in enumerate(exports):
  ti=Image.open(R/e['file']).convert('RGBA');ti=ti.resize((236,236),Image.Resampling.NEAREST);x=i%cols*250;y=i//cols*275;d.text((x+4,y+3),e['region'],fill='#173d35');qa.paste(ti,(x+4,y+30),ti)
 qp=H/'qa'/(stem+'-autotiles.png');qa.save(qp);write(qp.with_name(qp.name+'.derived.json'),{'file':qp.relative_to(R).as_posix(),'sha256':sha(qp),'operation':'Nearest enlarged engine atlas composite for inspection only','derivedFrom':[{'file':e['file'],'sha256':e['sha256']} for e in exports],'inspectionOnly':True});print(json.dumps({'stem':stem,'exported':len(exports),'qa':qp.relative_to(R).as_posix()}))
m['mappedCount']=len(m['assets']);write(mp,m);write(H/'inventory.json',inv)
