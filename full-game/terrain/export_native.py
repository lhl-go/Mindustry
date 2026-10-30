"""Persist actual-resolution crops, retaining generated detail without upscaling."""
from pathlib import Path
from PIL import Image
import numpy as np, json, hashlib, datetime, sys
H=Path(__file__).resolve().parent;R=H.parents[1];sys.path.insert(0,str(R/'records'))
from pixel_tools import components
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def periodic(a):
 a=a.astype(float);h,w=a.shape[:2];v=np.zeros_like(a);v[0]+=a[-1]-a[0];v[-1]+=a[0]-a[-1];v[:,0]+=a[:,-1]-a[:,0];v[:,-1]+=a[:,0]-a[:,-1]
 d=2*np.cos(2*np.pi*np.arange(h)/h)[:,None]+2*np.cos(2*np.pi*np.arange(w)/w)[None,:]-4;d[0,0]=1;s=np.fft.fft2(v,axes=(0,1))/d[:,:,None];s[0,0]=0;a-=np.fft.ifft2(s,axes=(0,1)).real
 for j in range(3):
  q=(3-j)/3;v=(a[:,j]+a[:,-1-j])/2;a[:,j]=(1-q)*a[:,j]+q*v;a[:,-1-j]=(1-q)*a[:,-1-j]+q*v
 for j in range(3):
  q=(3-j)/3;v=(a[j]+a[-1-j])/2;a[j]=(1-q)*a[j]+q*v;a[-1-j]=(1-q)*a[-1-j]+q*v
 return np.clip(np.rint(a),0,255).astype(np.uint8)
def main():
 m=json.loads((H/'manifest.json').read_text(encoding='utf8'));cache={};count=0
 for e in m['assets']:
  if e['artSource']=='official_retained_technical':
   e.update(nativeFile=e['file'],nativeSha256=e['sha256'],nativeSize=e['size'],nativeRecord=e['record'],nativeRole='unchanged official technical image; not AI art');continue
  if 'nativeFile' in e:continue
  rec=json.loads((R/e['record']).read_text(encoding='utf8'));op=rec['operation'];p=R/rec['derivedFrom'][0]['file'];box=op.get('sourceBBox')
  if not box:continue
  if p not in cache:cache[p]=Image.open(p).copy()
  im=cache[p];cut=im.crop(box);seam=None
  if op['type'].startswith('native_connected'):
   a=np.array(im.convert('RGBA'));stem=p.stem;receipt=json.loads((H/'records'/(stem+'.receipt.json')).read_text(encoding='utf8'));cols,rows=receipt['grid'];index=receipt['regions'].index(e['region']);mask=np.zeros(a.shape[:2],np.uint8)
   for c in components(a[:,:,3]>=16,min_area=16):
    x0,y0,x1,y1=c['bbox'];ci=min(rows-1,int((y0+y1)/2/im.height*rows))*cols+min(cols-1,int((x0+x1)/2/im.width*cols))
    if ci==index:
     for y,s,t in c['runs']:mask[y,s:t]=1
   a[:,:,3]=np.where(mask,a[:,:,3],0);a[:,:,3]=np.where(a[:,:,3]>=245,255,a[:,:,3]);a[a[:,:,3]==0,:3]=0;cut=Image.fromarray(a,'RGBA').crop(box)
   operation='connected-component native crop; alpha <16 removed, alpha >=245 snapped opaque, hidden RGB zeroed; no resize'
  else:
   a=periodic(np.array(cut.convert('RGB')));cut=Image.fromarray(a,'RGB');seam={'opposingEdgesByteEqual':bool(np.array_equal(a[0],a[-1]) and np.array_equal(a[:,0],a[:,-1])),'scope':'same native tile only; runtime mixing not verified'}
   operation='native crop with periodic-plus-smooth boundary correction and 3px edge pairing; no resize or new painted detail'
  dest=H/'native'/e['officialPath'];dest.parent.mkdir(parents=True,exist_ok=True);cut.save(dest)
  nr={'schemaVersion':1,'file':dest.relative_to(R).as_posix(),'sha256':sha(dest),'size':list(cut.size),'mode':cut.mode,'nativeResolution':True,'resized':False,'derivedFrom':[rec['derivedFrom'][0]],'sourceBBox':box,'operation':operation,'seamCheck':seam,'actualModel':None,'actualQuality':None,'modelEvidence':'Inherited source host generation; no model/quality metadata disclosed.'}
  write(dest.with_name(dest.name+'.derived.json'),nr)
  e.update(nativeFile=nr['file'],nativeSha256=nr['sha256'],nativeSize=nr['size'],nativeRecord=nr['file']+'.derived.json',nativeRole='AI material swatch only; engine connection geometry retained separately' if e['artSource']=='host_image_material_with_official_geometry' else 'native-resolution painted crop with authorized local cleanup')
  count+=1
 write(H/'manifest.json',m);print(json.dumps({'newNativeCrops':count,'totalNativeMapped':sum('nativeFile' in a for a in m['assets'])}))
if __name__=='__main__':main()
