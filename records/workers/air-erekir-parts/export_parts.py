from pathlib import Path
import sys,json,hashlib,datetime
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'records'))
from pixel_tools import components
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
PIVOTS={
 '01-air-weapons':[(220,305),(628,307),(1035,310),(220,700),(628,710),(1045,705),(220,1085),(627,1090),(1035,1100)],
 '02-ground-weapons':[(182,275),(528,285),(890,275),(1255,285),(180,620),(526,615),(892,620),(1260,630),(180,940),(526,985),(894,955),(1260,965)],
 '03-motion-defense':[(180,55),(527,51),(889,89),(1296,48),(183,376),(529,439),(919,386),(1282,359),(186,750),(759,773),(965,875),(1292,888)]
}
JOINTS={'leg-short-upper':[(180,55),(184,259)],'leg-short-lower':[(527,51),(527,265)],'leg-medium-upper':[(1296,48),(1294,276)],'leg-medium-lower':[(183,376),(181,644)],'leg-heavy-upper':[(919,386),(918,649)],'leg-heavy-lower':[(1282,359),(1279,642)]}
jobs=json.loads((HERE/'jobs.json').read_text(encoding='utf-8-sig'));assets=[];boards=[]
for job in jobs:
 stem=job['stem'];p=ROOT/'units/air-erekir-parts/source'/(stem+'.png')
 if not p.exists():continue
 receipt=json.loads((HERE/(stem+'.receipt.json')).read_text(encoding='utf-8'));job['args']=receipt['args']
 arr=np.array(Image.open(p).convert('RGBA'));h,w=arr.shape[:2];cols,rows=job['grid']
 cs=components(arr[:,:,3]>=16,100);assigned={}
 for c in cs:
  x0,y0,x1,y1=c['bbox'];idx=min(rows-1,int((y0+y1)/2/h*rows))*cols+min(cols-1,int((x0+x1)/2/w*cols))
  if idx in assigned:raise ValueError(f'Multiple large components in {stem} cell {idx}')
  assigned[idx]=c
 if len(assigned)!=len(job['regions']):raise ValueError(f'Missing region in {stem}: {len(assigned)}')
 boards.append({'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'nativeSize':[w,h],'generationRecord':p.relative_to(ROOT).as_posix()+'.generation.json','regions':job['regions']})
 for idx,region in enumerate(job['regions']):
  c=assigned[idx];x0,y0,x1,y1=c['bbox'];mask=np.zeros((h,w),bool)
  for y,s,e in c['runs']:mask[y,s:e]=True
  clean=np.zeros_like(arr);clean[mask]=arr[mask];crop=clean[y0:y1,x0:x1].copy();operations=[]
  # A material-specific alpha correction is permitted local pixel processing; RGB artwork is untouched.
  if region=='tecta-shield':
   rgb=crop[:,:,:3].astype(np.int16);jade=(rgb[:,:,1]>rgb[:,:,0]+4)&(rgb[:,:,2]>rgb[:,:,0])&(crop[:,:,3]>0)
   before=crop[:,:,3][jade].copy();crop[:,:,3][jade]=np.minimum(crop[:,:,3][jade],150)
   operations.append({'type':'make_existing_jade_shield_material_translucent','selector':'G > R+4 and B > R on retained shield pixels','alphaMax':150,'pixelsChanged':int(np.count_nonzero(before!=crop[:,:,3][jade])),'rgbUnchanged':True,'goldFrameAndCentralPivotPreserved':True})
  im=Image.fromarray(crop,'RGBA');px,py=PIVOTS[stem][idx];pivot=[px-x0,py-y0];joints=[[x-x0,y-y0] for x,y in JOINTS.get(region,[])]
  if region.startswith('foot-'):
   im=im.transpose(Image.Transpose.ROTATE_180);pivot=[im.width-1-pivot[0],im.height-1-pivot[1]]
   operations.append({'type':'rotate_180','reason':'Generated toes pointed south; lossless orientation normalization to north.','resampling':False})
  pad=32;canvas=Image.new('RGBA',(im.width+pad*2,im.height+pad*2));canvas.alpha_composite(im,(pad,pad));pivot=[v+pad for v in pivot];joints=[[x+pad,y+pad] for x,y in joints]
  dest=ROOT/'units/air-erekir-parts/assets'/(region+'.png');dest.parent.mkdir(parents=True,exist_ok=True);canvas.save(dest)
  src={'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'generationRecord':p.relative_to(ROOT).as_posix()+'.generation.json'}
  op={'type':'connected_component_extract_crop_pad','mask':'alpha >= 16; keep full connected component >=100 pixels; zero RGB outside retained alpha; no grid clipping','sourceBBox':c['bbox'],'sourceComponentArea':c['area'],'padding':pad,'pixelResampling':False,'additionalOperations':operations}
  rec={'schemaVersion':1,'file':dest.relative_to(ROOT).as_posix(),'createdAt':now(),'kind':'derived_image','tool':'local Pillow / NumPy','route':'user_authorized_pixel_processing','format':'PNG','mode':'RGBA','width':canvas.width,'height':canvas.height,'sha256':sha(dest),'derivedFrom':[src],'operation':op,'resized':False,'actualModel':None,'actualQuality':None,'modelEvidence':'Inherited source generation record; no model invoked for this processing.'}
  record=dest.with_name(dest.name+'.derived.json');write(record,rec)
  a=np.array(canvas);al=a[:,:,3];ys,xs=np.where(al>0)
  entry={'region':region,'id':region,'file':rec['file'],'sha256':rec['sha256'],'record':record.relative_to(ROOT).as_posix(),'source':src,'nativeExtractedSize':[im.width,im.height],'outputSize':[canvas.width,canvas.height],'sourceBBox':c['bbox'],'pivot':pivot,'pivotSpace':'output image pixels, top-left origin','pivotStatus':'estimated visual mounting axis; owner must register per unit','jointCenters':joints,'forward':'north' if region!='disrupt-tail' else 'hinge upper-right; single blade sweeps lower-left; mirror for opposite side','alphaExtrema':[int(al.min()),int(al.max())],'padding':min(int(xs.min()),int(ys.min()),canvas.width-1-int(xs.max()),canvas.height-1-int(ys.max())),'hiddenRgbPixels':int(np.count_nonzero(np.any(a[:,:,:3]!=0,axis=2)&(al==0))),'runtimeIntegrationVerified':False,'status':'exported_awaiting_visual_QA'}
  if region=='disrupt-tail':entry['officialRegionAlias']='disrupt-weapon-blade';entry['mappingNote']='Working art name only. Official movable part is Weapon RegionPart("-blade"), not UnitType tail; reusable as a designed rear-wing piece.'
  if region=='tecta-shield':entry['alphaCorrection']=operations;entry['translucentJadePixels']=int(np.count_nonzero((al>0)&(al<=150)))
  assets.append(entry)
write(HERE/'jobs.json',jobs)
manifest={'schemaVersion':1,'updatedAt':now(),'status':'exported_pending_visual_QA','scope':'33 independent regions only; body-only redraws and unit assembly owned by units_air_erekir','boards':boards,'assets':assets,'resized':False,'runtimeIntegrationVerified':False,'usage':'Owner may downsample and register these independent pieces; never upsample while claiming native detail.'}
write(HERE/'manifest.json',manifest)
qa=HERE/'qa';qa.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
for board in boards:
 selected=[a for a in assets if a['region'] in board['regions']]
 cols=3 if len(selected)==9 else 4;cw=520;ch=520
 sheet=Image.new('RGB',(cols*cw,((len(selected)+cols-1)//cols)*ch),'#ece7db');draw=ImageDraw.Draw(sheet)
 for n,a in enumerate(selected):
  im=Image.open(ROOT/a['file']).convert('RGBA');x=(n%cols)*cw;y=(n//cols)*ch
  # Native scale QA; if unusually large, increase cell rather than resample.
  if im.width>cw-12 or im.height>ch-32:raise ValueError('QA cell too small '+a['region'])
  bg=Image.new('RGBA',im.size,(30,42,40,255));ld=Image.new('RGBA',im.size,(242,236,220,255));bg.alpha_composite(im);ld.alpha_composite(im)
  # Split backdrop through same native sprite for fast comparison; no interpolation.
  bg.paste(ld.crop((im.width//2,0,im.width,im.height)),(im.width//2,0));sheet.paste(bg.convert('RGB'),(x+(cw-im.width)//2,y+28))
  draw.text((x+8,y+5),a['region'],fill='#173d35',font=font)
 qp=qa/(Path(board['file']).stem+'-contact.png');sheet.save(qp)
 write(qp.with_name(qp.name+'.derived.json'),{'file':qp.relative_to(ROOT).as_posix(),'sha256':sha(qp),'createdAt':now(),'operation':'Native-scale verification contact sheet; half dark and half light backgrounds alpha-composited, labels added; no resampling.','derivedFrom':[{'file':a['file'],'sha256':a['sha256'],'record':a['record']} for a in selected],'inspectionOnly':True})
print(json.dumps({'exported':len(assets),'boards':len(boards),'files':[a['file'] for a in assets]},ensure_ascii=False))
