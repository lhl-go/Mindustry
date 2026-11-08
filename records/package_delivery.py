from pathlib import Path
import zipfile,json,hashlib,datetime,os
ROOT=Path(__file__).resolve().parents[1]
check=json.loads((ROOT/'records/final-delivery-verification.json').read_text(encoding='utf-8'))
manifest=json.loads((ROOT/'exports/manifest.json').read_text(encoding='utf-8'))
assert check['passed'] and manifest['status']=='art_complete_runtime_unverified','All required art files and checks must pass before packaging.'
gallery=json.loads((ROOT/'records/delivery-browser-qa.json').read_text(encoding='utf-8'))
assert gallery.get('passed'),'Final offline gallery QA must pass before packaging.'
for source in gallery.get('sources',[]):
 assert hashlib.sha256((ROOT/source['file']).read_bytes()).hexdigest()==source['sha256'],'Gallery QA is stale: '+source['file']
out=ROOT/'exports/Mindustry-Daoist-Art-v160.7.zip';part=out.with_suffix('.zip.part')
exclusion_path=ROOT/'records/package-exclusions.json'
exclusion_data=json.loads(exclusion_path.read_text(encoding='utf-8')) if exclusion_path.exists() else {'files':[]}
excluded_files={x['file'] for x in exclusion_data['files']}
required_files={x['file'] for x in [*manifest['units'],*manifest['kit'],*manifest['concepts'],manifest['character']]}
required_files.update(f for u in manifest['units'] for f in u['layers'])
required_files.update(s[k] for g in manifest['ui'] for s in g['states'] for k in ['desktopPng','mobilePng'] if s.get(k))
assert not required_files.intersection(excluded_files),'Cannot omit any required delivery asset.'
excluded={'__pycache__','.git','.cache'}
files=[]
for base,dirs,names in os.walk(ROOT,followlinks=False):
 dirs[:]=[d for d in dirs if d not in excluded and not (Path(base)/d).is_symlink()]
 for name in names:
  p=Path(base)/name;rel=p.relative_to(ROOT).as_posix()
  if p.is_symlink() or p.suffix.lower() in {'.zip','.part','.pyc','.log','.pid'}:continue
  if rel in ['records/package-verification.json','exports/checksums.sha256']:continue
  if rel in excluded_files:continue
  files.append(p)
files.sort(key=lambda p:p.relative_to(ROOT).as_posix())
checksums=ROOT/'exports/checksums.sha256'
lines=[hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix() for p in files]
checksums.write_text('\n'.join(lines)+'\n',encoding='utf-8')
files.append(checksums)
with zipfile.ZipFile(part,'w',allowZip64=True) as z:
 for p in files:
  rel=p.relative_to(ROOT).as_posix()
  compression=zipfile.ZIP_STORED if p.suffix.lower() in {'.png','.jpg','.jpeg','.webp'} else zipfile.ZIP_DEFLATED
  z.write(p,'mindustry-image/'+rel,compress_type=compression,compresslevel=6 if compression==zipfile.ZIP_DEFLATED else None)
with zipfile.ZipFile(part) as z:
 bad=z.testzip();assert bad is None,bad;count=len(z.infolist())
part.replace(out)
record=dict(packagedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),file=out.relative_to(ROOT).as_posix(),bytes=out.stat().st_size,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),fileCount=count,crcVerified=True,entryPoint='mindustry-image/exports/index.html',checksums='mindustry-image/exports/checksums.sha256',excludedIntermediateImages=len(excluded_files),localIntermediateDeletionPending=bool(excluded_files),runtimeIntegrationVerified=False)
(ROOT/'records/package-verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
