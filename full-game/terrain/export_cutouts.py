from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,datetime,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT/'records'))
from pixel_tools import components
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inv=json.loads((HERE/'inventory.json').read_text(encoding='utf-8'));byregion={e['region']:e for e in inv['entries']};mp=HERE/'manifest.json';m=json.loads(mp.read_text(encoding='utf-8'))
for stem in sys.argv[1:]:
 p=HERE/'source'/(stem+'.png');r=json.loads((HERE/'records'/(stem+'.receipt.json')).read_text(encoding='utf-8'));im=Image.open(p).convert('RGBA');a=np.array(im);regions=r['regions'];cols,rows=r['grid'];groups=[[] for _ in regions]
 for c in components(a[:,:,3]>=16,min_area=16):
  x0,y0,x1,y1=c['bbox'];i=min(rows-1,int((y0+y1)/2/im.height*rows))*cols+min(cols-1,int((x0+x1)/2/im.width*cols))
  if i<len(groups):groups[i].append(c)
 exported=[]
 for i,region in enumerate(regions):
  e=byregion[region];cs=groups[i]
  if not cs:raise ValueError('Missing cutout '+region)
  box=[min(c['bbox'][0] for c in cs),min(c['bbox'][1] for c in cs),max(c['bbox'][2] for c in cs),max(c['bbox'][3] for c in cs)]
  box=[max(0,box[0]-2),max(0,box[1]-2),min(im.width,box[2]+2),min(im.height,box[3]+2)]
  mask=np.zeros((im.height,im.width),dtype=np.uint8)
  for c in cs:
   for y,s,t in c['runs']:mask[y,s:t]=1
  clean=a.copy();clean[:,:,3]=np.where(mask,clean[:,:,3],0);clean[:,:,3]=np.where(clean[:,:,3]>=245,255,clean[:,:,3]);clean[clean[:,:,3]==0,:3]=0
  native=Image.fromarray(clean,'RGBA').crop(box);target=e['originalSize'];pad=max(1,round(min(target)*.02));size=(target[0]-pad*2,target[1]-pad*2)
  if region=='yellowcoral-center':
   original=Image.open(HERE/e['officialSource']['file']).convert('RGBA');ob=original.getchannel('A').getbbox();size=(ob[2]-ob[0],ob[3]-ob[1]);pad=(target[0]-size[0])//2
  scale=min(size[0]/native.width,size[1]/native.height,1);outsize=[max(1,round(native.width*scale)),max(1,round(native.height*scale))];cut=native.resize(outsize,Image.Resampling.LANCZOS)
  out=Image.new('RGBA',target);out.alpha_composite(cut,((target[0]-cut.width)//2,(target[1]-cut.height)//2));oa=np.array(out);oa[oa[:,:,3]<4]=0;out=Image.fromarray(oa,'RGBA')
  dest=HERE/'assets'/e['officialPath'];dest.parent.mkdir(parents=True,exist_ok=True);out.save(dest)
  rec={'schemaVersion':1,'file':dest.relative_to(ROOT).as_posix(),'sha256':sha(dest),'createdAt':now(),'kind':'derived_image','width':out.width,'height':out.height,'format':'PNG','mode':'RGBA','derivedFrom':[{'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'generationRecord':p.relative_to(ROOT).as_posix()+'.generation.json'}],'operation':{'type':'native_connected_component_crop_alpha_cleanup_downsample_register','sourceBBox':box,'nativeExtractedSize':list(native.size),'nativeComponents':len(cs),'componentThresholdAlpha':16,'minimumComponentArea':16,'nearOpaqueAlphaSnappedAt':245,'filter':'Lanczos downsample only','contentScale':scale,'exportPadding':pad,'registeredCanvas':target,'noNewPaintedDetail':True},'actualModel':None,'actualQuality':None,'modelEvidence':'Inherited source generation; local authorized pixel cleanup only.'}
  write(dest.with_name(dest.name+'.derived.json'),rec)
  entry={'officialPath':e['officialPath'],'region':region,'file':rec['file'],'sha256':rec['sha256'],'record':rec['file']+'.derived.json','artSource':'host_image_derived','category':e['category'],'size':target,'nativeExtractedSize':list(native.size),'opaque':False,'alphaRange':[int(oa[:,:,3].min()),int(oa[:,:,3].max())],'status':'exported_needs_visual_alpha_review','runtimeIntegrationVerified':False}
  m['assets']=[x for x in m['assets'] if x['officialPath']!=entry['officialPath']]+[entry];exported.append(entry);e['status']=entry['status'];e['outputFile']=entry['file']
 qa=Image.new('RGB',(cols*360,rows*205),'#dad9cf');d=ImageDraw.Draw(qa)
 for i,e in enumerate(exported):
  tile=Image.open(ROOT/e['file']).convert('RGBA');tile.thumbnail((160,165),Image.Resampling.NEAREST)
  if max(tile.size)<160:tile=tile.resize((round(tile.width*160/max(tile.size)),round(tile.height*160/max(tile.size))),Image.Resampling.NEAREST)
  x=(i%cols)*360;y=(i//cols)*205;d.text((x+4,y+3),e['region'],fill='#173d35')
  for k,color in enumerate(['#f4ead8','#132a32']):
   bg=Image.new('RGBA',(176,178),color);bg.alpha_composite(tile,((176-tile.width)//2,(178-tile.height)//2));qa.paste(bg.convert('RGB'),(x+k*180,y+22))
 qp=HERE/'qa'/(stem+'-alpha.png');qa.save(qp);write(qp.with_name(qp.name+'.derived.json'),{'file':qp.relative_to(ROOT).as_posix(),'sha256':sha(qp),'operation':'True alpha composite on light and dark background, nearest enlarged for inspection only','derivedFrom':[{'file':e['file'],'sha256':e['sha256']} for e in exported],'inspectionOnly':True})
 print(json.dumps({'stem':stem,'exported':len(exported),'qa':qp.relative_to(ROOT).as_posix()}))
m['mappedCount']=len(m['assets']);m['updatedAt']=now();write(mp,m);write(HERE/'inventory.json',inv)
