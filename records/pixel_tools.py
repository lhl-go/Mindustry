import numpy as np
def components(mask,min_area=20):
    parent=[];runs=[];previous=[]
    def find(a):
        while parent[a]!=a:
            parent[a]=parent[parent[a]];a=parent[a]
        return a
    for y,row in enumerate(mask):
        edges=np.diff(np.r_[False,row,False].astype(np.int8));current=[]
        for s,e in zip(np.where(edges==1)[0],np.where(edges==-1)[0]):
            n=len(parent);parent.append(n)
            for ps,pe,pn in previous:
                if pe>=s and ps<=e:
                    a,b=find(n),find(pn)
                    if a!=b:parent[b]=a
            current.append((int(s),int(e),n));runs.append((y,int(s),int(e),n))
        previous=current
    groups={}
    for y,s,e,n in runs:
        root=find(n);g=groups.setdefault(root,dict(area=0,bbox=[s,y,e,y+1],runs=[]))
        g['area']+=e-s;g['bbox']=[min(g['bbox'][0],s),min(g['bbox'][1],y),max(g['bbox'][2],e),max(g['bbox'][3],y+1)];g['runs'].append((y,s,e))
    return [g for g in groups.values() if g['area']>=min_area]
