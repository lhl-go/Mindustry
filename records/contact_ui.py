from PIL import Image,ImageDraw
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
device=sys.argv[1] if len(sys.argv)>1 else 'desktop'
files=sorted((root/'ui/states').glob('*--s00--'+device+'.png'))
for i in range(0,len(files),15):
 out=Image.new('RGB',(1470,1500),'#ddd5bd');draw=ImageDraw.Draw(out)
 for j,p in enumerate(files[i:i+15]):
  im=Image.open(p);im.thumbnail((480,270));x=j%3*490;y=j//3*300
  out.paste(im,(x,y+25));draw.text((x+8,y+6),p.stem,fill='black')
 out.save(root/'records/preview-qa'/f'{device}-contact-{i//15}.jpg',quality=90)
