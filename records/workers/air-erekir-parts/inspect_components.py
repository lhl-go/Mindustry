from pathlib import Path
import sys,json,numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'records'))
from pixel_tools import components
data=[]
for p in sorted((ROOT/'units/air-erekir-parts/source').glob('*.png')):
 a=np.array(Image.open(p).convert('RGBA'));cs=components(a[:,:,3]>=16,100)
 hist=np.bincount(a[:,:,3].ravel(),minlength=256)
 data.append({'file':p.name,'size':[a.shape[1],a.shape[0]],'alphaMostCommon':sorted(enumerate(hist.tolist()),key=lambda x:-x[1])[:6],'components':[{'area':c['area'],'bbox':c['bbox']} for c in cs]})
(HERE/'components.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
print(json.dumps(data,indent=2))
