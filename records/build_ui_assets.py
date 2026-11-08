"""Copy approved skins and slice model-generated icons; no new artwork is drawn."""
from pathlib import Path
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageEnhance,ImageFont,ImageDraw
from pixel_tools import components
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'ui/kit';OUT.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
source_root=ROOT.parent/'designs/mail-ui-v1'
legacy=json.loads((source_root/'unity-slices/input-manifest.json').read_text(encoding='utf-8-sig'))
names=['window_frame','title_plate','button_primary','button_secondary','close_button','stat_field','tab_horizontal','notice_icon','round_badge_compass','round_badge_taiji']
entries=[]
for name in names:
    source=source_root/'assets'/(name+'.png');dest=OUT/(name+'.png');shutil.copyfile(source,dest)
    im=Image.open(dest);im.verify();im=Image.open(dest)
    old=next(x for x in legacy['assets'] if x['file']=='assets/'+name+'.png')
    rec=dict(file=dest.relative_to(ROOT).as_posix(),sha256=sha(dest),width=im.width,height=im.height,
      derivedFrom=dict(file='../designs/mail-ui-v1/assets/'+name+'.png',sha256=sha(source),sourceMapping='../designs/mail-ui-v1/unity-slices/input-manifest.json'),
      operation='byte_exact_copy_approved_skin',sourcePixelsUnchanged=True,actualModel=None,actualQuality=None,
      unverifiedReason='Reused existing approved art. Historical exact generation model not verified; not relabelled as a new GPT Image 2.5 generation.',
      borderLeftBottomRightTop=old['borderLeftBottomRightTop'],nativeSize=[im.width,im.height],resampled=False)
    dump(dest.with_name(dest.name+'.derived.json'),rec);entries.append(rec)
atlas=ROOT/'ui/components/ui-functional-icons-v1.png';im=Image.open(atlas).convert('RGBA')
keys=['search','filter','sort','refresh','close','settings','play','pause','save','folder','import','export','planet','research','blueprint','mods','database','network','drill','conveyor','furnace','power','turret','drone']
raw=np.array(im);parts=components(raw[:,:,3]>=16,min_area=28);groups={i:[] for i in range(24)}
for part in parts:
    x0,y0,x1,y1=part['bbox'];col=min(5,int(((x0+x1)/2)//256));row=min(3,int(((y0+y1)/2)//256));groups[row*6+col].append(part)
for idx,key in enumerate(keys):
    selected=groups[idx];assert selected,key
    box=(min(p['bbox'][0] for p in selected),min(p['bbox'][1] for p in selected),max(p['bbox'][2] for p in selected),max(p['bbox'][3] for p in selected))
    arr=np.array(im.crop(box));a=arr[:,:,3];keep=np.zeros(a.shape,dtype=bool)
    for part in selected:
        for y,s,e in part['runs']:keep[y-box[1],s-box[0]:e-box[0]]=True
    arr[:,:,3]=np.clip(np.rint((a.astype(float)-8)*255/237),0,255).astype(np.uint8);arr[~keep]=0
    clean=Image.fromarray(arr);bbox=clean.getbbox()
    assert bbox is not None,key
    crop=clean.crop(bbox);pad=8;canvas=Image.new('RGBA',(crop.width+pad*2,crop.height+pad*2));canvas.alpha_composite(crop,(pad,pad))
    dest=OUT/('icon-'+key+'.png');canvas.save(dest)
    rec=dict(file=dest.relative_to(ROOT).as_posix(),sha256=sha(dest),width=canvas.width,height=canvas.height,
      derivedFrom=dict(file=atlas.relative_to(ROOT).as_posix(),sha256=sha(atlas),generationRecord='ui/components/ui-functional-icons-v1.png.generation.json'),
      operation=dict(type='connected_component_group_crop_alpha_cleanup_and_padding',sourceBox=box,localAlphaBounds=bbox,padding=pad,alphaCutoff=16,minComponentArea=28,componentGrouping='by midpoint to six by four atlas cells; full components retained across grid lines',alphaRemap='clip(round((alpha-8)*255/237),0,255)',retainedRGBUnchanged=True),
      nativeSourceSize=[1536,1024],resampled=False,modelEvidence='Inherited from source; not new model generation',semanticKey=key)
    dump(dest.with_name(dest.name+'.derived.json'),rec);entries.append(rec)
# Existing HUD scene is reused only as a separately identified cropped scenery layer.
source=ROOT/'ui/01-factory-defense-hud-v1.png';box=(0,100,1320,655);dest=OUT/'factory-scene.png';Image.open(source).crop(box).save(dest)
rec=dict(file=dest.relative_to(ROOT).as_posix(),sha256=sha(dest),width=1320,height=555,
 derivedFrom=dict(file=source.relative_to(ROOT).as_posix(),sha256=sha(source),generationRecord='ui/01-factory-defense-hud-v1.png.generation.json'),
 operation=dict(type='crop',sourceBox=box),resampled=False,usage='illustrative gameplay background; UI text rebuilt independently')
dump(dest.with_name(dest.name+'.derived.json'),rec);entries.append(rec)
# Style state variants preserve the original painted shapes and native resolution.
for base in ('button_primary','button_secondary','tab_horizontal','stat_field'):
    source=OUT/(base+'.png');img=Image.open(source).convert('RGBA')
    for state,bright,sat in [('over',1.13,1),('down',.82,1),('disabled',.96,.15)]:
        alpha=img.getchannel('A');rgb=ImageEnhance.Color(img.convert('RGB')).enhance(sat);rgb=ImageEnhance.Brightness(rgb).enhance(bright);rgb.putalpha(alpha)
        dest=OUT/(base+'-'+state+'.png');rgb.save(dest)
        rec=dict(file=dest.relative_to(ROOT).as_posix(),sha256=sha(dest),width=img.width,height=img.height,
         derivedFrom=dict(file=source.relative_to(ROOT).as_posix(),sha256=sha(source),record=source.name+'.derived.json'),
         operation=dict(type='authorized_state_color_transform',brightness=bright,saturation=sat),resampled=False,state=state)
        dump(dest.with_name(dest.name+'.derived.json'),rec);entries.append(rec)
dump(OUT/'manifest.json',dict(schemaVersion=1,assets=entries,authorization='User explicitly authorized local pixel cleanup and slicing on 2026-10-26',runtimeIntegration='not_verified'))
# Annotated QA contact sheet is a derived inspection artifact, never a source texture.
sheet=Image.new('RGB',(1200,800),'#24393a');draw=ImageDraw.Draw(sheet)
for idx,key in enumerate(keys):
    icon=Image.open(OUT/('icon-'+key+'.png'));icon.thumbnail((160,145));x=(idx%6)*200+(200-icon.width)//2;y=(idx//6)*200+10
    sheet.paste(icon,(x,y),icon);draw.text(((idx%6)*200+10,(idx//6)*200+170),key,fill='#f5e9cf')
sheet.save(ROOT/'records/ui-icons-qa.jpg',quality=94)
print('Created',len(entries),'independent UI texture entries')
