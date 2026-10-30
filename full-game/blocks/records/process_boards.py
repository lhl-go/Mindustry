from pathlib import Path
from PIL import Image,ImageDraw
import json,re,hashlib,numpy as np,datetime,shutil,sys
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'full-game/blocks';PROJECT=ROOT.parent
sys.path.insert(0,str(ROOT/'records/workers/serpulo-ground-naval'))
from inspect_components import components
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return str(p.relative_to(ROOT)).replace('\\','/')
def write(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
plans=json.loads((OUT/'records/board-plans.json').read_text(encoding='utf-8'))
assets=[]; inventory=json.loads((OUT/'inventory.json').read_text(encoding='utf-8'));defs={x['id']:x for x in inventory['blocks']}
for plan in plans:
 name=plan['name'];rp=OUT/f'records/{name}.receipt.json'
 if not rp.exists():continue
 receipt=json.loads(rp.read_text(encoding='utf-8'));src=Path(re.search(r' as (.+\.png) by default',receipt['output_hint']).group(1))
 board=OUT/f'boards/{name}.png';board.parent.mkdir(exist_ok=True)
 if not board.exists():shutil.copy2(src,board)
 im=Image.open(board).convert('RGBA');ar=np.array(im);h,w=ar.shape[:2]
 gp=OUT/f'records/{name}.generation.json'
 if not gp.exists():
  write(gp,{'file':rel(board),'sha256':sha(board),'generatedAt':datetime.datetime.fromtimestamp(src.stat().st_mtime,datetime.timezone.utc).isoformat(),'width':w,'height':h,'format':'RGBA PNG','tool':'image_gen','route':'builtin','configSnapshot':json.loads((PROJECT/'config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'transparent_background':True},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed image_gen exposes no model/quality selector and returns no verifiable model/quality metadata.','evidence':{'receipt':rel(rp)},'prompt':rel(OUT/f'prompts/{name}.txt'),'references':[{'file':str(p.relative_to(PROJECT)).replace('\\','/'),'sha256':sha(p),'purpose':'primary user-confirmed art direction','actuallyAttached':True} for p in [PROJECT/'designs/mail-ui-v1/01-mail-event.png',PROJECT/'designs/team-ui-v2/team-ui-v2.png']],'sourceImageRetained':True})
 if plan.get('additionalReferences'):
  g=json.loads(gp.read_text(encoding='utf-8'))
  for f in plan['additionalReferences']:
   if not any(x['file']==f for x in g['references']):g['references'].append({'file':f,'sha256':sha(PROJECT/f),'purpose':'technical topology reference actually attached','actuallyAttached':True})
  write(gp,g)
 cols,rows=plan['grid']; previews=[]
 global_cc=[c for c in components(ar[:,:,3]>=16) if c[4]>1000]
 global_cc=sorted(global_cc,key=lambda c:-c[4])[:len(plan['ids'])]
 global_cc.sort(key=lambda c:(c[1]+c[3])/2)
 ordered=[]
 for row in range(rows):ordered+=sorted(global_cc[row*cols:(row+1)*cols],key=lambda c:(c[0]+c[2])/2)
 assert len(ordered)==len(plan['ids']),(name,len(ordered))
 for n,id in enumerate(plan['ids']):
  x0,y0,x1,y1=ordered[n][:4]
  cell=ar[y0:y1,x0:x1].copy();cell[cell[:,:,3]<16]=0;cell[:,:,3][cell[:,:,3]>=245]=255
  cc=components(cell[:,:,3]>0);keep=[c for c in cc if c[4]>=max(12,cc[0][4]*.0005)]
  mask=np.zeros(cell.shape[:2],bool)
  for c in keep:
   for xa,y,xb in c[5]:mask[y,xa:xb]=True
  cell[~mask]=0
  ys,xs=np.nonzero(mask);box=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
  crop=Image.fromarray(cell).crop(box);native=Image.new('RGBA',(crop.width+32,crop.height+32));native.alpha_composite(crop,(16,16))
  dst=OUT/f'masters/{id}.png';dst.parent.mkdir(exist_ok=True);native.save(dst)
  derived=Path(str(dst)+'.derived.json')
  write(derived,{'file':rel(dst),'sha256':sha(dst),'derivedFrom':[{'file':rel(board),'sha256':sha(board),'generationRecord':rel(gp)}],'operation':{'type':'authorized native alpha cleanup and crop','cellBox':[x0,y0,x1,y1],'subjectBoxInCell':box,'alphaBelow16':'clear RGBA','alphaAtLeast245':255,'removedTinyComponents':len(cc)-len(keep),'paddingPixels':16,'scale':1},'nativeSize':list(native.size),'anchorPixels':[native.width/2,native.height/2],'orientation':'north/up','artRole':plan.get('role','body'),'engineNotVerified':True})
  sourcepaths=defs.get(id,{}).get('requiredSourcePaths',[])
  assets.append({'id':id,'file':rel(dst),'sha256':sha(dst),'generationRecord':rel(derived),'layers':[{'file':rel(dst),'role':plan.get('role','body')}],'layerFiles':[rel(dst)],'nativeSize':list(native.size),'sourcePaths':sourcepaths,'status':'native_art_ready_mapping_pending','engineNotVerified':True})
  previews.append((id,native))
 for background,label in [((241,234,218),'light'),((32,42,46),'dark')]:
  contact=Image.new('RGB',(cols*320,rows*340),background);draw=ImageDraw.Draw(contact)
  for n,(id,native) in enumerate(previews):
   thumb=native.copy();thumb.thumbnail((296,296),Image.Resampling.LANCZOS);x=n%cols*320+(320-thumb.width)//2;y=n//cols*340+(310-thumb.height)//2
   contact.paste(thumb,(x,y),thumb);draw.text((n%cols*320+8,n//cols*340+316),id,fill=(80,80,70) if label=='light' else (220,220,210))
  cp=OUT/f'qa/{name}-{label}.jpg';cp.parent.mkdir(exist_ok=True);contact.save(cp,quality=94)
  write(Path(str(cp)+'.derived.json'),{'file':rel(cp),'sha256':sha(cp),'operation':'QA downscale and actual alpha compositing only','sourceInputs':[{'file':rel(OUT/f'masters/{id}.png'),'sha256':sha(OUT/f'masters/{id}.png')} for id,_ in previews]})
write(OUT/'manifest.json',{'schema':'mindustry-full-game-blocks-v1','status':'in_progress','requiredSourcePngCount':inventory['scope']['requiredSourcePngCount'],'blockCount':inventory['scope']['blockCount'],'nativeMasterCount':len(assets),'assets':assets})
print('Processed native masters',len(assets))
