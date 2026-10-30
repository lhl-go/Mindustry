"""Merge independent art domains by exact upstream source path, never by counts alone."""
import json,hashlib,collections
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inv=read(HERE/'inventory-all-source-images.json');expected={a['sourcePath']:a for a in inv['assets']}
cachepath=HERE/'verification-cache.json';cache=read(cachepath)if cachepath.exists()else{}
errors=[];mapped={};domains={};newcache={}
def check(path,digest):
    p=ROOT/path
    if not p.is_file():return ['missing:'+path]
    h=sha(p)
    if digest and h!=digest:return ['hash:'+path]
    if cache.get(path)==h:newcache[path]=h;return []
    if p.suffix.lower()in ['.png','.jpg','.jpeg','.webp','.ico','.icns']:
        try:
            im=Image.open(p);im.verify()
        except Exception as e:return ['decode:'+path+':'+str(e)]
    newcache[path]=h;return []
for domain in ['ui-system','items-fx','terrain','root-turrets','units','blocks']:
    p=HERE/domain/'manifest.json'
    if not p.exists():domains[domain]={'status':'pending','mapped':0};continue
    m=read(p);rows=m.get('sourceMappings',m.get('mappings',m.get('assets',[])))
    originalSizes={}
    if domain=='terrain':originalSizes={a['officialPath']:a.get('originalSize')for a in read(HERE/domain/'inventory.json')['entries']}
    elif domain=='blocks':originalSizes={a['sourcePath']:a.get('sourceDimensions')for a in read(HERE/domain/'inventory.json')['sourceFiles']}
    count=0
    for a in rows:
        source=a.get('sourcePath',a.get('officialPath'))
        if not source:continue # Native masters are not completed source-path exports.
        file=a.get('engineFile',a.get('outputFile',a.get('file')))
        if not file:continue
        digest=a.get('engineSha256',a.get('sha256'))
        if source not in expected:errors.append('unexpected_source:'+source);continue
        if source in mapped:errors.append('duplicate_source:'+source);continue
        err=check(file,digest);errors.extend(err)
        dims=a.get('sourceDimensions',a.get('officialSize',a.get('sourceSize',originalSizes.get(source))))
        if dims and Path(file).suffix.lower()=='.png'and (ROOT/file).exists():
            if list(Image.open(ROOT/file).size)!=list(dims):errors.append('source_canvas:'+source)
        if a.get('file') and a['file']!=file:errors.extend(check(a['file'],a.get('sha256')))
        native=a.get('nativeFile',a.get('file'))
        if domain=='ui-system':
            stem=Path(source).stem
            for catalog in ['icons-manifest.json','sectors-manifest.json']:
                for v in read(HERE/domain/catalog)['assets']:
                    if v.get('semanticKey')==stem:native=v['file']
            if native==file and a.get('derivedFrom'):
                candidate=a['derivedFrom'][0]['file']
                if '/reference/'not in candidate:native=candidate
        nativeDigest=a.get('nativeSha256')
        if not nativeDigest:
            if native==a.get('file'):nativeDigest=a.get('sha256')
            for origin in a.get('derivedFrom',[]):
                if origin.get('file')==native:nativeDigest=origin.get('sha256')
        if native:errors.extend(check(native,nativeDigest))
        mapped[source]={'sourcePath':source,'sourceGitBlob':expected[source]['sourceGitBlob'],'domain':domain,'file':file,'sha256':sha(ROOT/file)if (ROOT/file).exists()else None,'nativeFile':native,'nativeSha256':sha(ROOT/native)if native and (ROOT/native).exists()else None,'disposition':a.get('disposition',a.get('artKind',a.get('artSource',a.get('plan','domain_manifest')))),'status':a.get('status',m.get('status')),'domainManifest':p.relative_to(ROOT).as_posix(),'runtimeIntegrationVerified':False}
        count+=1
    domains[domain]={'status':m.get('status'),'mapped':count,'manifestSha256':sha(p)}
additional=[]
if (HERE/'units/manifest.json').exists():
    u=read(HERE/'units/manifest.json')
    for a in u.get('additionalAtlasRegions',[])+u.get('generatedAtlasRegions',[]):
        errors.extend(check(a['file'],a['sha256']));additional.append({'id':a['id'],'file':a['file'],'sha256':a['sha256'],'domain':'units','copyIntoSourceTree':a.get('copyIntoSourceTree',False)})
fx=read(HERE/'items-fx/runtime-atlas.json')
for a in fx['exported']+fx.get('closedInputs',[]):
    errors.extend(check(a['file'],a['sha256']));additional.append({'id':a.get('id','fluid-stencil'),'file':a['file'],'sha256':a['sha256'],'domain':'items-fx','copyIntoSourceTree':False})
missing=sorted(set(expected)-set(mapped));byowner=collections.Counter(expected[p]['owner']for p in missing)
notready=[d for d,v in domains.items()if not v['status']or not (v['status'].startswith('art_export_complete') or v['status'].startswith('complete_') or v['status']=='complete')]
result={'sourceCommit':inv['referenceCommit'],'checkedAt':datetime.now(timezone.utc).isoformat(),'status':'all_source_images_verified'if not(errors or missing or notready)else'in_progress','requiredSourceImages':len(expected),'mappedSourceImages':len(mapped),'missingSourceImages':len(missing),'domains':domains,'missingByOwner':dict(byowner),'notReadyDomains':notready,'errors':errors,'missing':missing,'assets':[mapped[k]for k in sorted(mapped)],'additionalVerifiedExports':additional,'additionalVerifiedExportCount':len(additional),'runtimeIntegrationVerified':False}
(HERE/'coverage.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');cachepath.write_text(json.dumps(newcache,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items()if k not in ['assets','missing','additionalVerifiedExports']},ensure_ascii=False))
