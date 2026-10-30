from build import *
from qa import make_contact

m=rd(B/'manifest.json')
extra=[]
for name,file in m['additionalPaintedComponents'].items():
 im=Image.open(R/file)
 extra.append(dict(id=name,file=file,role='native_painted_component',size=list(im.size)))
extra+=m['additionalAtlasRegions']
for label,bg in [('dark',(28,39,38)),('light',(245,240,222))]:
 make_contact(extra,B/'qa'/f'additional-{label}.png',bg)

frames=m['generatedAtlasRegions'];groups={}
for f in frames:groups.setdefault(f['id'].rsplit('-',1)[0],[]).append(f)
sheet=Image.new('RGB',(1080,len(groups)*180),(28,39,38));draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12)
for row,(name,fs) in enumerate(groups.items()):
 draw.text((4,row*180+4),name,font=font,fill=(235,235,215))
 for col,f in enumerate(fs):
  im=Image.open(R/f['file']).convert('RGBA');im=im.resize((38,min(130,im.height)),Image.Resampling.NEAREST)
  tile=Image.new('RGBA',(50,140),(28,39,38,255));tile.alpha_composite(im,((50-im.width)//2,(140-im.height)//2));sheet.paste(tile.convert('RGB'),(col*60,row*180+22));draw.text((col*60+20,row*180+164),str(col),font=font,fill=(200,210,200))
p=B/'qa/treads-frames.png';sheet.save(p)
wr(Path(str(p)+'.generation.json'),dict(file=rel(p),sha256=sha(p),operation='QA only: official one-pixel-wide runtime tread frames widened for pixel inspection; engine files unchanged',derivedFrom=[srcinfo(R/a['file']) for a in frames]))
print(json.dumps({'additional':len(extra),'treadGroups':len(groups),'frames':len(frames)}))
