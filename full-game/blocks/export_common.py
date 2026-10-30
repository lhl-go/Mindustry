"""Small shared exporter for disjoint, explicitly assigned building categories."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageOps,ImageDraw
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rel=lambda p:Path(p).relative_to(ROOT).as_posix()
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
INV=read(HERE/'inventory.json');HANDOFF={a['sourcePath']for a in read(HERE/'turrets-handoff.json')['sourceFiles']}
ROWS={a['region']:a for a in INV['sourceFiles']if a['sourcePath']not in HANDOFF}
DEFS={a['id']:a for a in INV['blocks']}
def original(row):
 p=HERE/'reference-sprites'/row['sourcePath'].removeprefix('core/assets-raw/sprites/')
 assert p.is_file()and sha(p)==row['sourceSha256'],row['region']
 return p,Image.open(p).convert('RGBA')
def master(name):
 p=HERE/'masters'/(name+'.png');assert p.is_file(),'Missing native master '+name
 return p,Image.open(p).convert('RGBA')
def fit(native,template,box=None):
 """Fit accepted native pixels to original alpha placement, never add painted detail."""
 box=box or template.getchannel('A').getbbox()or(0,0,*template.size)
 source=native.crop(native.getchannel('A').getbbox());size=(box[2]-box[0],box[3]-box[1]);scaled=ImageOps.contain(source,size,Image.Resampling.LANCZOS)
 out=Image.new('RGBA',template.size);out.alpha_composite(scaled,(box[0]+(size[0]-scaled.width)//2,box[1]+(size[1]-scaled.height)//2));return out
def neutral_mask(alpha):
 a=np.asarray(alpha,dtype=np.uint8);out=np.full((*a.shape,4),255,dtype=np.uint8);out[:,:,3]=a;out[a==0]=0;return Image.fromarray(out)
def save(row,out,native,operation,*,disposition='derived_from_styled_art',extra_sources=None):
 op,orig=original(row);assert out.size==orig.size,(row['region'],out.size,orig.size)
 native=Path(native);assert native.is_file()
 p=HERE/'compat'/row['sourcePath'];p.parent.mkdir(parents=True,exist_ok=True)
 if disposition=='exact_upstream_technical_reuse':p.write_bytes(op.read_bytes())
 else:out.save(p)
 record={'sourcePath':row['sourcePath'],'sourceGitBlob':row['sourceGitBlob'],'sourceSha256':row['sourceSha256'],'sourceDimensions':list(orig.size),'region':row['region'],'blockId':row['blockId'],'category':row['category'],'file':rel(p),'sha256':sha(p),'engineFile':rel(p),'engineSha256':sha(p),'nativeFile':rel(native),'nativeSha256':sha(native),'nativeSize':list(Image.open(native).size),'sourceAlphaBounds':list(orig.getchannel('A').getbbox()or(0,0,*orig.size)),'operation':operation,'disposition':disposition,'derivedFrom':[{'file':rel(native),'sha256':sha(native)},{'file':rel(op),'sha256':sha(op)}]+(extra_sources or []),'actualModel':None,'actualQuality':None,'runtimeIntegrationVerified':False,'status':'exported_pending_static_review'}
 record['record']=rel(p)+'.derived.json';write(ROOT/record['record'],record);return record
def finish_batch(name,categories,rows,review=None):
 expected={a['sourcePath']for a in ROWS.values()if a['category']in categories};actual={a['sourcePath']for a in rows}
 assert len(actual)==len(rows)and actual==expected,{'missing':sorted(expected-actual),'extra':sorted(actual-expected)}
 for a in rows:
  assert sha(ROOT/a['file'])==a['sha256']and sha(ROOT/a['nativeFile'])==a['nativeSha256']
  im=Image.open(ROOT/a['file']);assert list(im.size)==a['sourceDimensions'];im.verify()
 result={'ownerBatch':name,'categories':categories,'checkedAt':datetime.now(timezone.utc).isoformat(),'sourceMappings':rows,'sourceCount':len(rows),'errors':[],'status':'exported_pending_visual_review','review':review,'runtimeIntegrationVerified':False}
 write(HERE/'batches'/(name+'.json'),result);return result
def contact(rows,name,cols=6):
 """Inspection aid only; preserve actual alpha over light and dark backgrounds."""
 paths=[]
 for start in range(0,len(rows),48):
  group=rows[start:start+48];canvas=Image.new('RGB',(cols*220,((len(group)+cols-1)//cols)*260),(225,223,210));d=ImageDraw.Draw(canvas)
  for i,a in enumerate(group):
   im=ImageOps.contain(Image.open(ROOT/a['file']).convert('RGBA'),(102,212),Image.Resampling.NEAREST);x=i%cols*220;y=i//cols*260
   for dx,bg in [(0,(245,237,219)),(110,(25,45,47))]:
    d.rectangle((x+dx,y,x+dx+107,y+221),fill=bg);canvas.paste(im,(x+dx+(108-im.width)//2,y+(220-im.height)//2),im)
   d.text((x+3,y+226),a['region'][:33],fill=(30,50,45))
  p=HERE/'qa'/(name+'-'+str(start//48+1).zfill(2)+'.png');p.parent.mkdir(exist_ok=True);canvas.save(p);paths.append(rel(p))
 return paths
