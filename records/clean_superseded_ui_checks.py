from pathlib import Path
import json,hashlib,re,datetime
ROOT=Path(__file__).resolve().parents[1]
report=json.loads((ROOT/'records/ui-render-all.json').read_text(encoding='utf-8'))
assert len(report['records'])==616 and not report['errors']
assert all(not r['checks']['images'] and not r['checks']['outsideControls'] and not any(r['checks']['rootOverflow']) for r in report['records'])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
removed=[]
for folder in ['records/workers/ui-audit/screenshots','records/workers/final-audit/screenshots']:
 base=(ROOT/folder).resolve();assert base.is_relative_to(ROOT.resolve())
 for p in base.glob('*.png'):
  m=re.fullmatch(r'((?:UI|D|C)-\d+)-(\d+)-(desktop|mobile)\.png',p.name)
  if not m:continue
  gid,state,device=m.groups();replacement=ROOT/f'ui/states/{gid}--s{int(state):02d}--{device}.png'
  assert replacement.is_file()
  removed.append(dict(file=p.relative_to(ROOT).as_posix(),sha256=sha(p),replacedBy=replacement.relative_to(ROOT).as_posix(),reason='Final frozen-input capture supersedes interim layout check'))
  p.unlink()
for name in ['C-01.png','D-01.png','desktop-contact-0.jpg','desktop-contact-1.jpg']:
 p=ROOT/'records/preview-qa'/name
 if p.exists():
  removed.append(dict(file=p.relative_to(ROOT).as_posix(),sha256=sha(p),replacedBy='records/ui-render-all.json',reason='Interim preview superseded by complete frozen-input state captures'));p.unlink()
out=dict(cleanedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),removed=removed,retained='Final ui/states paired PNGs; unique scroll-position QA PNGs; final delivery gallery captures; all historical text provenance',rule='Only verified superseded image files in this task were removed. No recursive directory deletion.')
(ROOT/'records/superseded-ui-image-cleanup.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(removed=len(removed))))
