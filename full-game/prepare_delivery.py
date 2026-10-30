"""Freeze only verified final art, required source records, previews and integration files."""
import json,hashlib,os,re
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent.parent;HERE=ROOT/'full-game'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    coverage=read(HERE/'coverage.json');assert coverage['status']=='all_source_images_verified',coverage['notReadyDomains']
    assert not coverage['errors'] and coverage['mappedSourceImages']==2368
    gallery=read(HERE/'qa/gallery-review.json');assert gallery['passed']
    for s in gallery['sources']:assert sha(ROOT/s['file'])==s['sha256'],s['file']
    files={'ATTRIBUTION.md'};excluded={a['file']for a in read(ROOT/'records/package-exclusions.json')['files']}
    for p in HERE.glob('*/retention-cleanup.json'):
        for a in read(p).get('files',[]):
            if a.get('excludeFromDeliveryArchive'):excluded.add(a['file'])
    # Keep the accepted first-scope assets, now a subset of the full-game package.
    for line in (ROOT/'exports/checksums.sha256').read_text(encoding='utf-8-sig').splitlines():
        old,p=line.split('  ',1);q=ROOT/p
        assert q.is_file(),p
        if p!='README.md':assert sha(q)==old,'Changed initial-scope file: '+p
        if p not in excluded:files.add(p)
    # Current metadata and algorithms are required evidence; cached upstream art is not delivery art.
    textExt={'.json','.md','.txt','.java','.py','.js','.html','.frag','.vert','.pe','.properties','.hjson','.xml','.csv','.yml','.yaml','.gradle'}
    for p in HERE.rglob('*'):
        if not p.is_file()or p.is_symlink()or '__pycache__'in p.parts:continue
        if p.name in ['delivery-files.json','package-verification.json','verification-cache.json']:continue
        if p.parent.name=='batches'and p.name in ['root-working.json','hud-working.json']:continue
        if p.suffix.lower()in textExt:files.add(p.relative_to(ROOT).as_posix())
    mediaExt={'.png','.jpg','.jpeg','.webp','.apng','.svg','.icns','.ico','.woff','.ttf'}
    def add(path):
        if not isinstance(path,str)or Path(path).suffix.lower()not in mediaExt:return
        p=ROOT/path
        if not p.is_file():return
        if path in excluded:raise AssertionError('Required file excluded: '+path)
        files.add(path)
    for a in coverage['assets']:
        add(a['file']);add(a.get('nativeFile'))
    # Explicit final asset directories; source boards/reference images remain omitted.
    directories=['root-turrets/masters','ui-system/controls','ui-system/special','ui-system/brand','units/parts','project-instructions']
    for directory in directories:
        for p in (HERE/directory).rglob('*'):
            if p.is_file():add(p.relative_to(ROOT).as_posix())
    for catalog in ['ui-system/icons-manifest.json','ui-system/sectors-manifest.json']:
        for a in read(HERE/catalog)['assets']:add(a['file'])
    for domain in ['blocks','terrain','items-fx','units','root-turrets']:
        m=read(HERE/domain/'manifest.json')
        for collection in ['assets','nativeMasters','additionalAtlasRegions','generatedAtlasRegions','integrationGeometryInputs']:
            for a in m.get(collection,[]):
                for key in ['file','engineFile','nativeFile']:add(a.get(key))
                for file in a.get('layerFiles',[]):add(file)
        # Current QA images document acceptance and are not superseded source art.
        for p in (HERE/domain/'qa').glob('*'):
            if p.is_file()and p.relative_to(ROOT).as_posix()not in excluded:add(p.relative_to(ROOT).as_posix())
    for p in (HERE/'ui-system/qa').glob('*'):
        if p.is_file():add(p.relative_to(ROOT).as_posix())
    for p in (HERE/'qa').glob('*'):
        if p.is_file():add(p.relative_to(ROOT).as_posix())
    for a in read(HERE/'runtime-visuals/manifest.json')['assets']:add(a['file'])
    for p in (HERE/'items-fx').glob('*.apng'):add(p.relative_to(ROOT).as_posix())
    # Include additional bubble/splash masks referenced in runtime atlas metadata.
    def strings(v):
        if isinstance(v,str):yield v
        elif isinstance(v,list):
            for x in v:yield from strings(x)
        elif isinstance(v,dict):
            for x in v.values():yield from strings(x)
    for value in strings(read(HERE/'items-fx/runtime-atlas.json')):
        if value.startswith('full-game/items-fx/')and '/source/'not in value and '/references/'not in value:add(value)
    # Font glyph and code evidence files may refer to upstream images that were used only as geometry references.
    omitted=[]
    for p in HERE.rglob('*'):
        rel=p.relative_to(ROOT).as_posix()
        if p.is_file()and p.suffix.lower()in mediaExt and rel not in files:
            omitted.append({'file':rel,'sha256':sha(p),'localFilePresent':True,'deliveryImageIncluded':False,'reason':'Reference, consumed generation board, superseded crop or internal contact; final mapped assets and text provenance are retained.'})
    for name in ['root-source-cleanup.json','root-unit-source-cleanup.json']:
        cleanup=HERE/name
        if cleanup.exists():
            for a in read(cleanup)['files']:
                p=Path(a.get('absolutePath',a['file']));assert not p.exists();rel=p.relative_to(ROOT).as_posix()
                omitted.append({'file':rel,'sha256':a['sha256'],'localFilePresent':False,'deliveryImageIncluded':False,'reason':'Consumed source image removed after final art verification under the explicit retention policy; generation metadata retained.'})
    knownOmissions={a['file']for a in omitted}
    for cleanup in HERE.glob('*/retention-cleanup.json'):
        for a in read(cleanup).get('files',[]):
            rel=a.get('file')
            if not rel or not a.get('excludeFromDeliveryArchive')or rel in knownOmissions:continue
            assert rel not in files,'Final file incorrectly scheduled for retention exclusion: '+rel
            omitted.append({'file':rel,'sha256':a.get('sha256'),'localFilePresent':(ROOT/rel).exists(),'deliveryImageIncluded':False,'reason':a.get('reason','Consumed source excluded under domain retention record.'),'retentionRecord':cleanup.relative_to(ROOT).as_posix()})
            knownOmissions.add(rel)
    retention={'policy':'Final art and needed design/integration evidence only; consumed reference/source boards are omitted from delivery. Some local deletions were rejected by automatic approval and have not been retried.','files':omitted}
    (HERE/'source-retention.json').write_text(json.dumps(retention,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');files.add('full-game/source-retention.json')
    assert not any(p.startswith('.work/')or p.endswith(('.zip','.pyc','.log','.pid'))for p in files)
    secret=re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
    for rel in files:
        p=ROOT/rel
        assert p.is_file() and p.resolve().is_relative_to(ROOT.resolve()),'Outside frozen project: '+rel
        assert not p.is_symlink(),'Symlink is not a frozen regular file: '+rel
        assert p.name not in ['.env','.git-credentials','id_rsa','id_ed25519'],'Credential file: '+rel
        if p.suffix.lower()in textExt:
            assert not secret.search(p.read_bytes()),'Credential-like content in '+rel
    report={'frozenAt':datetime.now(timezone.utc).isoformat(),'status':'frozen_verified_full_game_art','sourceCommit':coverage['sourceCommit'],'sourcePaths':2368,'runtimeIntegrationVerified':False,'fileCount':len(files),'totalBytes':sum((ROOT/p).stat().st_size for p in files),'files':[{'file':p,'bytes':(ROOT/p).stat().st_size,'sha256':sha(ROOT/p)}for p in sorted(files)],'excludedIntermediateImages':len(omitted),'entryPoint':'full-game/index.html'}
    (HERE/'delivery-files.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items()if k!='files'}))
if __name__=='__main__':main()
