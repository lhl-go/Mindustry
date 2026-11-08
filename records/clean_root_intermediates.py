"""Retain verified game PNGs; remove explicitly identified transient source pictures."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
special=read(ROOT/'records/workers/special/manifest.json')
# Verify all final special layers and composites before any source-image deletion.
retained=[]
for a in special['assets']:
 for item in [a,*a.get('layerFiles',[])]:
  f=item.get('file') if isinstance(item,dict) else item
  if not f:continue
  p=ROOT/f;Image.open(p).verify();retained.append(f)
  if isinstance(item,dict) and item.get('sha256'):assert sha(p)==item['sha256'],f
out=Image.new('RGB',(1600,1320),'#efe9db');draw=ImageDraw.Draw(out)
for i,a in enumerate(special['assets']):
 x=i%4*400;y=i//4*440;im=Image.open(ROOT/a['file']);im.thumbnail((185,380))
 for side,bg in enumerate(['#eee8d7','#20312f']):
  out.paste(bg,(x+side*200,y,x+(side+1)*200,y+440));out.paste(im,(x+side*200+(200-im.width)//2,y+40),im)
 draw.text((x+10,y+10),a['id'],fill='#1d4238')
out.save(ROOT/'records/workers/special/final-alpha-contact.jpg',quality=95)
targets=['characters/02-alchemy-engineer-v1.png','ui/components/ui-functional-icons-v1.png','units/root-builders/boards/01-core-builders-parts-v1.png','records/character-original-dark-inspection.jpg']
targets += [b['file'] for b in special['boards']]
targets += [p.relative_to(ROOT).as_posix() for p in (ROOT/'records/workers/special/qa').glob('*.png')]
targets += [p.relative_to(ROOT).as_posix() for p in (ROOT/'records/preview-qa').glob('UI-*.png')]
removed=[]
for f in targets:
 p=(ROOT/f).resolve();assert p.is_relative_to(ROOT.resolve()),p
 if not p.is_file():continue
 # This task never follows external links for cleanup.
 assert not p.is_symlink(),p
 removed.append(dict(file=f,sha256=sha(p),bytes=p.stat().st_size,reason='Final game export and source text record verified; source/intermediate picture no longer needed.'))
 p.unlink()
 for suffix in ['.generation.json','.derived.json']:
  rec=Path(str(p)+suffix)
  if rec.exists():d=read(rec);d.update(imageRetained=False,retentionReason='Removed after final export verification per user retention rule.');dump(rec,d)
for a in special['assets']:
 a['sourceImagesRetained']=False
 if isinstance(a.get('visualReview'),dict):a['visualReview']['individualQaImagesRetained']=False;a['visualReview']['retainedContactSheet']='records/workers/special/final-alpha-contact.jpg'
for b in special['boards']:b['imageRetained']=False
special['retention']=dict(sourceImagesRetained=False,finalContactSheet='records/workers/special/final-alpha-contact.jpg',reason='Source image and intermediate cleanup after final PNG verification; provenance text and hashes retained.')
dump(ROOT/'records/workers/special/manifest.json',special)
for p in (ROOT/'units/root-builders/layers').glob('*.derived.json'):
 d=read(p);d['sourceImageRetained']=False;dump(p,d)
p=ROOT/'records/workers/root-builders/manifest.json';d=read(p);d['board']['imageRetained']=False;d['sourceImagesRetained']=False;dump(p,d)
dump(ROOT/'records/final-root-image-cleanup.json',dict(cleanedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),removed=removed,kept='Final exported PNGs, current concept pages, both designated style references, current QA contacts, provenance text and source mappings.',outsideTaskPathsTouched=False))
print('Removed verified transient images:',len(removed),'bytes:',sum(x['bytes'] for x in removed))
