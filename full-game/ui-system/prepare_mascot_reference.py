from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).resolve().parent
c=Image.new('RGB',(1024,512),'#e8e2d2');d=ImageDraw.Draw(c)
for i,n in enumerate(['alphaaaa','ranai']):
 im=Image.open(p/f'reference/core/assets-raw/sprites/ui/{n}.png').convert('RGBA');im.thumbnail((400,400));im=im.resize((400,400),Image.Resampling.NEAREST);c.paste(im,(i*512+56,32),im);d.text((i*512+70,460),n,fill='black')
c.save(p/'reference/mascot-guide.png')
