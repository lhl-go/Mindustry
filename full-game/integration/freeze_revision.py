"""Freeze a new explicitly changed batch; never change an upload already in flight."""
from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2];HERE=ROOT/'full-game'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 previous=json.loads((HERE/'delivery-files.json').read_text(encoding='utf-8'))
 coverage=json.loads((HERE/'coverage.json').read_text(encoding='utf-8'));assert coverage['status']=='all_source_images_verified'and not coverage['errors']
 runtime=json.loads((HERE/'integration/qa/runtime-acceptance.json').read_text(encoding='utf-8'));assert runtime['passed']
 files={a['file']for a in previous['files']}
 excluded={'full-game/ui-system/brand/title-logo.png','full-game/ui-system/source/06-title-logo.png'}
 files-=excluded
 for directory in ['branding/tiangong-xianzhen','full-game/integration']:
  for p in (ROOT/directory).rglob('*'):
   if not p.is_file()or '__pycache__'in p.parts:continue
   if p.name in ['logo-v1.png','logo-v2.png','record_logo.py','finish_logo.py']:continue
   files.add(p.relative_to(ROOT).as_posix())
 files.add('records/local-intermediate-cleanup-20261028.json')
 for p in HERE.glob('ui-system/compat/**/logo.png.derived.json'):files.add(p.relative_to(ROOT).as_posix())
 files.discard('full-game/checksums.sha256');files.discard('full-game/package-verification.json');files.discard('full-game/delivery-files.json')
 for name in files:assert (ROOT/name).is_file(),name
 gallery=json.loads((HERE/'qa/gallery-review.json').read_text(encoding='utf-8'));assert gallery['passed']
 for a in gallery['sources']:assert sha(ROOT/a['file'])==a['sha256']
 rows=[{'file':name,'bytes':(ROOT/name).stat().st_size,'sha256':sha(ROOT/name)}for name in sorted(files)]
 changed=[a['file']for a in rows if next((o['sha256']for o in previous['files']if o['file']==a['file']),None)!=a['sha256']]
 r={'frozenAt':datetime.now(timezone.utc).isoformat(),'status':'frozen_verified_full_game_art','sourceCommit':coverage['sourceCommit'],'sourcePaths':2368,'runtimeIntegrationVerified':False,'desktopRuntimeAcceptancePassed':True,'runtimeAcceptance':'full-game/integration/qa/runtime-acceptance.json','fileCount':len(rows),'totalBytes':sum(a['bytes']for a in rows),'files':rows,'excludedIntermediateImages':previous.get('excludedIntermediateImages',0),'entryPoint':'full-game/index.html','gameTitle':'天工仙阵','revisionReason':'Approved Chinese title/logo, supported runtime art module, actual desktop render acceptance and refreshed 616 UI state captures.','changedPaths':changed,'excludedSupersededBrandImages':sorted(excluded),'allPlatformRuntimeVerified':False}
 (HERE/'delivery-files.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in r.items()if k not in ['files','changedPaths']},ensure_ascii=False))
if __name__=='__main__':main()
