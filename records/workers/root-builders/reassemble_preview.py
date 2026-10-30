from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mp=ROOT/'records/workers/root-builders/manifest.json';m=read(mp);retired=[]
for a in m['assets']:
 if a['id']!='gamma':continue
 uid=a['id'];bodyfile=next(l['file'] for l in a['layers'] if l['role']=='body');weaponfile=next(l['file'] for l in a['layers'] if l['role']=='weapon_mirrored_pair')
 body=Image.open(ROOT/bodyfile).convert('RGBA');weapon=Image.open(ROOT/weaponfile).convert('RGBA');weapon=weapon.crop(weapon.getbbox())
 visiblew=body.width-64;visibleh=body.height-64;ww=round(visiblew*.25);weapon=weapon.resize((ww,round(weapon.height*ww/weapon.width)),Image.Resampling.LANCZOS)
 # Registered art attachment points, explicitly separate from official gameplay offsets.
 xdelta=round(visiblew*.24);baseY=round(32+visibleh*(.235 if uid=='gamma' else .35));poses=[]
 underlay=Image.new('RGBA',body.size);visible=[];ba=np.array(body.getchannel('A'),dtype=float)/255
 for sign in [-1,1]:
  x=round(body.width/2+sign*xdelta-weapon.width/2);y=round(baseY-weapon.height*.82)
  assert x>=32 and y>=32 and x+weapon.width<=body.width-32 and y+weapon.height<=body.height-32
  layer=Image.new('RGBA',body.size);layer.alpha_composite(weapon,(x,y));wa=np.array(layer.getchannel('A'),dtype=float)/255
  ratio=float((wa*(1-ba)).sum()/wa.sum());visible.append(ratio);underlay.alpha_composite(layer);poses.append(dict(side=sign,topLeftPixels=[x,y],size=list(weapon.size),mountPivotNormalized=[.5,.82],visibleFractionAfterBody=ratio))
 underlay.alpha_composite(body)
 file=f'units/root-builders/assets/{uid}-v3.png';p=ROOT/file;underlay.save(p)
 rec=dict(file=file,sha256=sha(p),width=body.width,height=body.height,mode='RGBA',derivedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),derivedFrom=[dict(file=f,sha256=sha(ROOT/f),generationRecord=f+'.derived.json') for f in [bodyfile,weaponfile]],operation=dict(kind='static_art_mount_composite',order=['weapon_pair','body'],bodyResampled=False,weaponDownsampled=True,redrawn=False,placements=poses),actualModel=None,actualQuality=None,alignmentEvidence='Estimated art attachment anchors adjusted to expose the weapon tips. These are design coordinates, not validated official runtime Weapon.x/y.',runtimeIntegrationVerified=False)
 dump(Path(str(p)+'.derived.json'),rec)
 old=ROOT/a['file'];retired.append(dict(file=a['file'],sha256=sha(old),reason='Superseded by v2 composite with visible weapon tips. Native body and weapon layers unchanged.'));old.unlink()
 oldrec=ROOT/a['generationRecord'];d=read(oldrec);d.update(imageRetained=False,supersededBy=file);dump(oldrec,d)
 a.update(file=file,generationRecord=file+'.derived.json',sha256=sha(p),size=list(body.size),layerAlignment=dict(type='estimated_art_alignment',artAttachmentPlacements=poses,officialOffsetsRetainedInLayerMetadata=True,requiresRuntimeRegistration=True),visualReview='pending_v2_contact')
dump(mp,m)
out=Image.new('RGB',(1200,900));draw=ImageDraw.Draw(out)
for i,a in enumerate(m['assets']):
 im=Image.open(ROOT/a['file']);im.thumbnail((365,385))
 for j,color in enumerate(['#eee8d7','#20312f']):
  x=i*400;y=j*450;out.paste(color,(x,y,x+400,y+450));out.paste(im,(x+(400-im.width)//2,y+35),im);draw.text((x+16,y+12),a['id']+' final',fill='#213e32' if j==0 else '#eadcba')
out.save(ROOT/'records/workers/root-builders/final-alpha-contact.jpg',quality=95)
dump(ROOT/'records/workers/root-builders/gamma-v3-revision.json',dict(revisedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),reason='Gamma v3 exposes barrels using documented art anchor estimates.',retiredImages=retired))
print([(a['id'],[round(p['visibleFractionAfterBody'],3) for p in a['layerAlignment']['artAttachmentPlacements']]) for a in m['assets']])
