import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
handoff=read(ROOT/'full-game/blocks/turrets-handoff.json');files=handoff['sourceFiles'];regions={a['region']for a in files}
for folder in ['reference','source','prompts','records','masters','compat','qa']: (HERE/folder).mkdir(parents=True,exist_ok=True)
art=[];derived=[]
for a in files:
    rel=a['sourcePath'].split('core/assets-raw/sprites/')[1];ref=ROOT/'full-game/blocks/reference-sprites'/rel
    a['localReference']=ref.relative_to(ROOT).as_posix();assert ref.exists(),ref
    im=Image.open(ref).convert('RGBA');a['sourceAlphaBounds']=list(im.getbbox())
    a['sourceSha256']=hashlib.sha256(ref.read_bytes()).hexdigest()
    n=a['region']
    if a['role']=='heat-mask':a['plan']='derive_heat_mask_from_new_art'
    elif n.endswith('-liquid'):a['plan']='retain_white_liquid_fill_mask_aligned_to_canvas'
    elif n.endswith('-preview'):a['plan']='assemble_new_parts_in_source_canvas'
    elif n.endswith('-r')and n[:-1]+'l'in regions:a['plan']='mirror_generated_left_part';a['mirrorOf']=n[:-1]+'l'
    elif n in ['cyclone-barrel-2','cyclone-barrel-3']:a['plan']='translate_generated_cyclone_barrel_1';a['deriveFrom']='cyclone-barrel-1'
    else:a['plan']='generate_unique_region';art.append(a)
    if a['plan']!='generate_unique_region':derived.append(a)
# Keep adjacent members of each turret together; use 12 regions per 4x3 board.
art.sort(key=lambda a:('0-base'if a['blockId']is None else a['blockId'],a['region']))
batches=[]
for start in range(0,len(art),12):
    batch=art[start:start+12];n=start//12+1;cols=4;rows=(len(batch)+3)//4
    guide=Image.new('RGB',(cols*360,rows*360),'#e9e5d9');d=ImageDraw.Draw(guide)
    for i,a in enumerate(batch):
        im=Image.open(ROOT/a['localReference']).convert('RGBA');box=im.getbbox();crop=im.crop(box);scale=min(290/crop.width,280/crop.height);crop=crop.resize((round(crop.width*scale),round(crop.height*scale)),Image.Resampling.NEAREST)
        x=i%cols*360;y=i//cols*360;guide.paste(crop,(x+(360-crop.width)//2,y+24+(280-crop.height)//2),crop);d.text((x+14,y+322),a['region'],fill='#183830')
    gp=HERE/'reference'/f'guide-{n:02d}.png';guide.save(gp)
    batches.append({'batch':n,'grid':[cols,rows],'guide':gp.relative_to(ROOT).as_posix(),'regions':[a['region']for a in batch]})
(HERE/'inventory.json').write_text(json.dumps({'status':'in_progress','sourceCount':len(files),'turretCount':28,'uniqueArtRegions':len(art),'derivedRegions':len(derived),'assets':files,'blocks':handoff['blocks']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(HERE/'batches.json').write_text(json.dumps(batches,indent=2)+'\n')
print(json.dumps({'sourceCount':len(files),'uniqueArtRegions':len(art),'derivedRegions':len(derived),'batches':batches}))
