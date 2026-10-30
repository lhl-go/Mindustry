"""Crop only the last two accepted source boards, preserving native pixels and evidence."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,re,hashlib,numpy as np,sys,shutil
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'full-game/blocks';PROJECT=ROOT.parent
sys.path.insert(0,str(ROOT/'records/workers/serpulo-ground-naval'))
from inspect_components import components
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rel=lambda p:Path(p).relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,o):p=Path(p);p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
heads=['spore-press-piston-part','chemical-combustion-chamber-piston-part','pyrolysis-generator-piston-part','pyrolysis-generator-piston-t-part','radar-head-part','build-tower-head-part','repair-point-head-part','repair-turret-head-part','mass-driver-head-part','payload-mass-driver-head-part','large-payload-mass-driver-head-part','payload-mass-driver-left-part','large-payload-mass-driver-left-part','payload-mass-driver-cap-part','large-payload-mass-driver-cap-part','unit-repair-tower-head-part']
plans=[{'name':'moving-heads-pistons-02','grid':[4,4],'ids':heads},read(OUT/'records/root-parts-request.json')]
choice=sys.argv[1]if len(sys.argv)>1 else 'all'
snapshot=read(OUT/'records/moving-rotors-01.generation.json')['configSnapshot']
existing=read(OUT/'parts-manifest.json')if(OUT/'parts-manifest.json').exists()else{'assets':[],'boards':[]}
assets={a['id']:a for a in existing['assets']};boards={b['name']:b for b in existing['boards']}
for plan in plans:
 name=plan['name']
 if choice!='all'and choice!=name:continue
 rp=OUT/f'records/{name}.receipt.json';receipt=read(rp);hint=receipt.get('output_hint',receipt.get('resultMetadata',{}).get('output_hint'))
 src=Path(receipt.get('originalOutputPath')or re.search(r' as (.+\.png) by default',hint).group(1));assert src.is_file()
 sourceHash=sha(src)
 if receipt.get('imagePayload'):assert sourceHash==receipt['imagePayload']['sha256']
 board=OUT/f'boards/{name}.png'
 if board.exists():assert sha(board)==sourceHash
 else:shutil.copyfile(src,board)
 im=Image.open(board).convert('RGBA');ar=np.array(im);height,width=ar.shape[:2]
 gp=OUT/f'records/{name}.generation.json';refs=[]
 for p in [PROJECT/'designs/mail-ui-v1/01-mail-event.png',PROJECT/'designs/team-ui-v2/team-ui-v2.png']:
  refs.append({'file':p.relative_to(PROJECT).as_posix(),'sha256':sha(p),'purpose':'user-confirmed style','actuallyAttached':True,'attachmentEvidence':'original production prompt and parent task receipt'})
 if name=='root-detached-parts-03':
  p=OUT/'records/parts-source-contact.png';refs.append({'file':rel(p),'sha256':sha(p),'purpose':'technical part topology only','actuallyAttached':True,'attachmentEvidence':'root-parts-request.json and parent tool call'})
 write(gp,{'file':rel(board),'sha256':sourceHash,'generatedAt':datetime.fromtimestamp(src.stat().st_mtime,timezone.utc).isoformat(),'timestampEvidence':'Host output file modification time; exact service generation timestamp not disclosed.','width':width,'height':height,'format':'RGBA PNG','tool':'image_gen','route':'builtin','configSnapshot':snapshot,'configTargetEvidence':'Same production-batch target recorded in moving-rotors-01.generation.json; not proof of actual tool model selection.','submittedParameters':{'model':None,'quality':None,'transparent_background':True},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed built-in route exposes neither model/quality selectors nor actual returned model/quality metadata.','evidence':{'receipt':rel(rp),'receiptSha256':sha(rp),'originalOutputPath':str(src)},'prompt':rel(OUT/f'prompts/{name}.txt'),'references':refs,'sourceImageRetained':True})
 cols,rows=plan['grid'];cc=[c for c in components(ar[:,:,3]>=16)if c[4]>1000];assert len(cc)==len(plan['ids']),(name,len(cc))
 cc.sort(key=lambda c:(c[1]+c[3])/2);ordered=[]
 for row in range(rows):ordered+=sorted(cc[row*cols:(row+1)*cols],key=lambda c:(c[0]+c[2])/2)
 previews=[]
 for idx,(id,c)in enumerate(zip(plan['ids'],ordered)):
  x0,y0,x1,y1=c[:4];cell=ar[y0:y1,x0:x1].copy();cell[cell[:,:,3]<16]=0;cell[:,:,3][cell[:,:,3]>=245]=255
  groups=components(cell[:,:,3]>0);cutoff=max(12,groups[0][4]*.0005);keep=[v for v in groups if v[4]>=cutoff];mask=np.zeros(cell.shape[:2],bool)
  for v in keep:
   for xa,y,xb in v[5]:mask[y,xa:xb]=True
  cell[~mask]=0;ys,xs=np.nonzero(mask);box=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
  crop=Image.fromarray(cell).crop(box);native=Image.new('RGBA',(crop.width+32,crop.height+32));native.alpha_composite(crop,(16,16))
  dst=OUT/f'masters/{id}.png';assert not dst.exists()or id in assets,'Do not overwrite another worker master: '+id
  native.save(dst);record=Path(str(dst)+'.derived.json')
  touch={'left':int(np.count_nonzero(ar[y0:y1,0,3]>=16))if x0==0 else 0,'top':int(np.count_nonzero(ar[0,x0:x1,3]>=16))if y0==0 else 0,'right':int(np.count_nonzero(ar[y0:y1,-1,3]>=16))if x1==width else 0,'bottom':int(np.count_nonzero(ar[-1,x0:x1,3]>=16))if y1==height else 0}
  note='Source has three alpha>=16 pixels at the uppermost decorative apex. All four nozzle modules are present;16px padding adds no missing art or generated detail.'if id=='core-thruster-large-part'else None
  derived={'file':rel(dst),'sha256':sha(dst),'derivedAt':datetime.now(timezone.utc).isoformat(),'derivedFrom':[{'file':rel(board),'sha256':sourceHash,'generationRecord':rel(gp)}],'operation':{'type':'authorized native alpha cleanup and crop','cellBox':[x0,y0,x1,y1],'subjectBoxInCell':box,'alphaBelow16':'clear RGBA','alphaAtLeast245':255,'removedTinyComponents':len(groups)-len(keep),'paddingPixels':16,'scale':1,'newPaintedDetail':False},'nativeSize':list(native.size),'anchorPixels':[native.width/2,native.height/2],'artRole':'independent_detached_part','actualModel':None,'actualQuality':None,'orientation':'native source orientation retained; compatibility exporter must match the fixed renderer convention','sourceEdgeContactPixels':touch,'sourceEdgeNote':note,'engineNotVerified':True}
  write(record,derived)
  a={'id':id,'file':rel(dst),'sha256':sha(dst),'generationRecord':rel(record),'layers':[{'file':rel(dst),'role':'moving-part'}],'layerFiles':[rel(dst)],'nativeSize':list(native.size),'status':'native_art_ready_static_review_pending','engineNotVerified':True,'sourceEdgeNote':note};assets[id]=a;previews.append((id,native))
 for label,bg in [('light',(241,234,218)),('dark',(32,42,46))]:
  qa=Image.new('RGB',(cols*340,rows*360),bg);draw=ImageDraw.Draw(qa)
  for idx,(id,native)in enumerate(previews):
   thumb=native.copy();thumb.thumbnail((314,310),Image.Resampling.LANCZOS);x=idx%cols*340+(340-thumb.width)//2;y=idx//cols*360+(320-thumb.height)//2;qa.paste(thumb,(x,y),thumb);draw.text((idx%cols*340+6,idx//cols*360+330),id[:46],fill=(60,65,60)if label=='light'else(228,228,220))
  qp=OUT/f'qa/{name}-{label}.jpg';qa.save(qp,quality=95);write(Path(str(qp)+'.derived.json'),{'file':rel(qp),'sha256':sha(qp),'operation':'QA compositing/downscale only; not native art','sourceInputs':[{'file':assets[id]['file'],'sha256':assets[id]['sha256']}for id,_ in previews]})
 boards[name]={'name':name,'file':rel(board),'sha256':sourceHash,'generationRecord':rel(gp),'nativePartCount':len(previews),'ids':plan['ids']}
 print(json.dumps({'board':name,'parts':len(previews),'ids':plan['ids']}),flush=True)
 result={'schema':'mindustry-detached-native-parts-v1','status':'native_art_ready_static_review_pending','nativePartCount':len(assets),'assets':list(assets.values()),'boards':list(boards.values()),'runtimeIntegrationVerified':False}
 write(OUT/'parts-manifest.json',result)
