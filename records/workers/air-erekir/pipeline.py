from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFont
import numpy as np
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o): Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def connected(mask):
    h,w=mask.shape
    labels=np.zeros((h,w),np.int32)
    parents=[0]
    def root(x):
        while parents[x]!=x:
            parents[x]=parents[parents[x]];x=parents[x]
        return x
    previous=[]
    for y in range(h):
        row=np.pad(mask[y].astype(np.int8),(1,1));diff=np.diff(row)
        starts=np.where(diff==1)[0];ends=np.where(diff==-1)[0]
        current=[];pi=0
        for a,b in zip(starts,ends):
            a=int(a);b=int(b);i=len(parents);parents.append(i)
            while pi<len(previous) and previous[pi][1]<a:pi+=1
            pj=pi
            while pj<len(previous) and previous[pj][0]<=b:
                pa,pb,pid=previous[pj]
                ra,rb=root(i),root(pid)
                if ra!=rb:parents[rb]=ra
                pj+=1
            labels[y,a:b]=i;current.append((a,b,i))
        previous=current
    lut=np.array([root(i) for i in range(len(parents))],dtype=np.int32)
    labels=lut[labels];ids,counts=np.unique(labels,return_counts=True)
    comps=[]
    for i,n in zip(ids,counts):
        if i==0 or n<100:continue
        ys,xs=np.where(labels==i)
        comps.append(dict(label=int(i),area=int(n),bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]))
    return labels,sorted(comps,key=lambda c:-c['area'])
def inspect_components():
    out=[]
    for p in sorted((ROOT/'units/air-erekir/source').glob('*.png')):
        im=Image.open(p).convert('RGBA');arr=np.array(im)
        labels,comps=connected(arr[:,:,3]>=32)
        out.append(dict(file=p.name,components=comps[:30]))
    write(HERE/'components.json',out)
    print(json.dumps(out,indent=2))
if __name__=='__main__':inspect_components()
