import sys,json
from pathlib import Path
import numpy as np
from PIL import Image
root=Path(r'D:\work\image\mindustry-image');sys.path.insert(0,str(root/'records'))
from pixel_tools import components
p=root/'units/special/boards/01-drones-target-v1.png'
im=Image.open(p).convert('RGBA');a=np.array(im);cs=sorted(components(a[:,:,3]>=16,20),key=lambda c:c['area'],reverse=True)
print(json.dumps([{'area':c['area'],'bbox':c['bbox']} for c in cs[:15]]))
for name,color in [('dark',(28,36,39,255)),('light',(240,236,224,255))]:
    bg=Image.new('RGBA',im.size,color);bg.alpha_composite(im);bg.convert('RGB').save(root/f'records/workers/special/qa/drones-{name}.png')
