import sys,json
from pathlib import Path
import numpy as np
from PIL import Image
root=Path(r'D:\work\image\mindustry-image');sys.path.insert(0,str(root/'records'))
from pixel_tools import components
for p in sorted((root/'units/special/boards').glob('*.png')):
    im=Image.open(p).convert('RGBA');a=np.array(im);cs=sorted(components(a[:,:,3]>=16,20),key=lambda c:c['area'],reverse=True)
    print(json.dumps({'file':p.stem,'size':im.size,'components':[{'area':c['area'],'bbox':c['bbox']} for c in cs[:16]]}))
