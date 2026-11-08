from pathlib import Path
from PIL import Image
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
copies=[('mail-ui-reference.png','designs/mail-ui-v1/01-mail-event.png'),('team-ui-reference.png','designs/team-ui-v2/team-ui-v2.png')]
for name,src in copies:
 p=ROOT/'references/style'/name;im=Image.open(p)
 dump(Path(str(p)+'.derived.json'),dict(file=p.relative_to(ROOT).as_posix(),width=im.width,height=im.height,sha256=sha(p),operation='byte_exact_copy_of_user_designated_style_reference',derivedFrom=dict(file='../'+src,sha256=sha(ROOT.parent/src)),actualModel=None,actualQuality=None,modelEvidence='Existing approved reference; historical exact model and quality not relabeled.',copiedFor='Portable task handoff'))
kit=ROOT/'ui/kit/manifest.json';assets=read(kit)['assets']
for report in (ROOT/'records').glob('ui-render-*.json'):
 d=read(report);d['sourceAssetManifest']=dict(file='ui/kit/manifest.json',sha256=sha(kit),purpose='Raster skins, icons, scene crop available to the captured HTML/CSS; each asset has its own provenance.');d['actualModel']=None;d['actualQuality']=None;d['modelEvidence']='Browser composites are not new AI generations. Original AI evidence is in linked kit sources.';dump(report,d)
for p in (ROOT/'ui/kit').glob('*.derived.json'):
 d=read(p)
 source=d.get('derivedFrom')
 if isinstance(source,dict) and source.get('file')=='ui/components/ui-functional-icons-v1.png':d['sourceImageRetained']=False;dump(p,d)
p=ROOT/'characters/02-alchemy-engineer-clean.png.derived.json';d=read(p);d['sourceImageRetained']=False;dump(p,d)
reviews=[]
for worker in ['special','root-builders']:
 for p in (ROOT/f'records/workers/{worker}').glob('*contact.jpg'):
  m=read(ROOT/f'records/workers/{worker}/manifest.json');files=set(a['file'] for a in m['assets'])
  if 'weapon' in p.name:files={l['file'] for a in m['assets'] for l in a['layers'] if 'weapon' in l['file']}
  im=Image.open(p);reviews.append(dict(file=p.relative_to(ROOT).as_posix(),sha256=sha(p),width=im.width,height=im.height,operation='Downscaled visual QA contact on light/dark opaque backgrounds; not a game sprite or new generated art.',derivedFrom=[dict(file=f,sha256=sha(ROOT/f)) for f in sorted(files)],actualModel=None,actualQuality=None))
dump(ROOT/'records/derived-review-images.json',dict(recordedAt=now,images=reviews))
print('Portable references and render/source lineage indexed.')
