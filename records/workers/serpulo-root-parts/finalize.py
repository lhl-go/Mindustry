from pathlib import Path
from PIL import Image
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=ROOT/'records/workers/serpulo-root-parts';mp=base/'manifest.json';m=json.loads(mp.read_text(encoding='utf-8'))
checks=[]
for a in m['assets']:
 p=ROOT/a['file'];im=Image.open(p);alpha=im.getchannel('A');bbox=alpha.getbbox()
 assert sha(p)==a['sha256'] and bbox[0]>=32 and bbox[1]>=32 and bbox[2]<=im.width-32 and bbox[3]<=im.height-32
 checks.append(dict(file=a['file'],sha256=sha(p),nativePixelExtraction=True,clearBorderPx=32,bodyOnlyReviewed=True))
qa=base/'final-alpha-contact.jpg';qrec=dict(file=qa.relative_to(ROOT).as_posix(),sha256=sha(qa),operation='Two-background contact sheet of actual exported PNGs; downsampled for visual QA only',derivedFrom=checks,visualResult='passed: coherent full silhouettes, no retained gun barrels or EMP weapons, alpha edges clean on light and dark backgrounds; Aegires energy field retained',runtimeIntegrationVerified=False)
qa.with_name(qa.name+'.derived.json').write_text(json.dumps(qrec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
removed=[]
for version in ['v1','v2']:
 p=ROOT/f'units/serpulo-root-parts/14-support-hulls-{version}.png';rec=p.with_name(p.name+'.generation.json')
 if p.exists():
  assert p.resolve().is_relative_to((ROOT/'units/serpulo-root-parts').resolve())
  removed.append(dict(file=p.relative_to(ROOT).as_posix(),sha256=sha(p),reason='Final native-resolution hull PNGs and complete provenance verified; intermediate generation board removed per retention policy'))
  p.unlink()
 d=json.loads(rec.read_text(encoding='utf-8'));d.update(imageRetained=False,status='superseded_weapon_removal_incomplete' if version=='v1' else 'consumed_by_verified_native_layer_exports',finalAssets=[a['file'] for a in m['assets']] if version=='v2' else []);rec.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m.update(sourceImageRetained=False,visualQAStatus='passed',verification='records/workers/serpulo-root-parts/verification.json');mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(base/'verification.json').write_text(json.dumps(dict(checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),passed=True,assets=checks,removedSourceImages=removed,runtimeIntegrationVerified=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(verified=len(checks),removed=len(removed))))
