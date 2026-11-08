from pathlib import Path
from PIL import Image
import numpy as np
from scipy import ndimage
import json
root=Path(__file__).resolve().parents[3]
out=[]
for p in sorted((root/'units/air-erekir/source').glob('*.png')):
 a=np.array(Image.open(p).convert('RGBA'))[:,:,3]
 labels,count=ndimage.label(a>=32)
 bounds=ndimage.find_objects(labels)
 sizes=np.bincount(labels.ravel())
 rows=[]
 for index,b in enumerate(bounds,1):
  if b and sizes[index]>200:
   y,x=b; rows.append(dict(label=index,area=int(sizes[index]),bbox=[x.start,y.start,x.stop,y.stop]))
 out.append(dict(file=p.name,components=sorted(rows,key=lambda z:-z['area'])))
print(json.dumps(out,indent=2))
(Path(__file__).parent/'components.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
