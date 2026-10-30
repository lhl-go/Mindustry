from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
import json, hashlib
HERE=Path(__file__).resolve().parent.parent
ROOT=HERE.parent.parent
inv=json.loads((HERE/'inventory.json').read_text(encoding='utf-8-sig'))
rows={r['region']:r for r in inv['sourceFiles']}
names=[r['region'] for r in inv['sourceFiles'] if r['region'].startswith('core-') and '-thruster' in r['region']]
names += ['mass-driver-base','mass-driver','bridge-conveyor-bridge','phase-conveyor-bridge','duct-bridge-bridge','bridge-conduit-bridge','phase-conduit-bridge','reinforced-bridge-conduit-bridge']
sheet=Image.new('RGB',(1050,len(names)*180),(32,42,46));draw=ImageDraw.Draw(sheet)
checks=[]
for idx,name in enumerate(names):
    row=rows[name];rel=row['sourcePath'];original=HERE/'reference-sprites'/rel.removeprefix('core/assets-raw/sprites/');export=HERE/'compat'/rel
    meta=json.loads(Path(str(export)+'.derived.json').read_text(encoding='utf-8-sig'))
    native=ROOT/meta['nativeFile']
    y=idx*180
    draw.text((3,y+4),name,fill='white')
    for col,(label,p) in enumerate([('upstream',original),('native',native),('compat',export)]):
        image=Image.open(p).convert('RGBA');image=ImageOps.contain(image,(300,145),Image.Resampling.NEAREST)
        x=col*350+(350-image.width)//2
        sheet.paste(image,(x,y+28+(145-image.height)//2),image)
        draw.text((col*350+4,y+17),label,fill=(180,200,200))
    checks.append({'region':name,'original':str(original),'native':str(native),'compat':str(export),'sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'operation':meta['operation']})
for start in range(0,len(names),6):
    sheet.crop((0,start*180,1050,min(start+6,len(names))*180)).save(HERE/('qa/core-thruster-audit-contact-'+str(start//6+1)+'.jpg'),quality=95)
(HERE/'qa/core-thruster-audit-inputs.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'rows':len(names),'names':names}))
