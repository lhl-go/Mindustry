from pathlib import Path
from PIL import Image
import numpy as np,json

def components(mask):
    runs=[]; parent=[]; previous=[]
    def find(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]];i=parent[i]
        return i
    for y,row in enumerate(mask):
        d=np.diff(np.r_[False,row,False].astype(np.int8)); starts=np.where(d==1)[0]; ends=np.where(d==-1)[0]
        current=[]; pi=0
        for x0,x1 in zip(starts.tolist(),ends.tolist()):
            n=len(runs);runs.append((x0,y,x1,y+1));parent.append(n);current.append(n)
            while pi<len(previous) and runs[previous[pi]][2]<x0:pi+=1
            for oi in previous[pi:]:
                if runs[oi][0]>x1:break
                a=find(n);b=find(oi)
                if a!=b:parent[a]=b
        previous=current
    groups={}
    for i,(x0,y,x1,y1) in enumerate(runs):
        r=find(i)
        if r not in groups:groups[r]=[x0,y,x1,y1,0,[]]
        g=groups[r];g[0]=min(g[0],x0);g[1]=min(g[1],y);g[2]=max(g[2],x1);g[3]=max(g[3],y1);g[4]+=x1-x0;g[5].append((x0,y,x1))
    return sorted(groups.values(),key=lambda g:-g[4])

if __name__=='__main__':
    out={}
    for p in Path('units/serpulo-ground-naval/boards').glob('*.png'):
        a=np.array(Image.open(p))[:,:,3]; cs=components(a>=16)
        out[p.stem]=[c[:5] for c in cs if c[4]>100]
        print(p.stem,out[p.stem])
    Path('records/workers/serpulo-ground-naval/components.json').write_text(json.dumps(out,indent=2))
