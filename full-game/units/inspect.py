from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
R=Path(__file__).resolve().parents[2];B=R/'full-game/units';a=json.loads((B/'audit.json').read_text())['assets'];ref={x['region']:R/'full-game/units/reference'/x['sourcePath'] for x in a};names=['dagger-base','corvus-base','crawler-base','atrax-base','arkyid-joint-base','toxopid-joint-base','atrax-joint','corvus-joint','disrupt-missile-fin','disrupt-weapon-preview','obviate-preview','power-cell'];paths=[(x,ref[x]) for x in names]+[('new leg-light',R/'units/serpulo-ground-naval/parts/leg-light.png'),('new leg-upper',R/'units/serpulo-ground-naval/parts/leg-upper.png'),('new disrupt-weapon',R/'units/air-erekir-parts/assets/disrupt-weapon.png'),('new disrupt-fin',R/'units/special/layers/disrupt-missile-left-fin.png')];sheet=Image.new('RGB',(1200,4*220),(45,52,50));d=ImageDraw.Draw(sheet)
for i,(name,p) in enumerate(paths):
 im=Image.open(p).convert('RGBA');im=im.crop(im.getbbox());im.thumbnail((260,175));bg=Image.new('RGBA',(280,180),(45,52,50,255));bg.alpha_composite(im,((280-im.width)//2,(180-im.height)//2));x=i%4*300;y=i//4*220;sheet.paste(bg.convert('RGB'),(x+10,y+5));d.text((x+10,y+190),name,fill='white')
sheet.save(B/'source-part-inspection.png')
