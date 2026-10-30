"""Inventory non-image visual dependencies from the same verified upstream tree."""
import json,hashlib,concurrent.futures,urllib.request,time
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent.parent;HERE=ROOT/'full-game/runtime-visuals'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
tree=read(ROOT/'records/reference-ui-sources/official-tree-v160.7.json')['tree'];by={x['path']:x for x in tree}
COMMIT='17012d61d9e4c3cbd9820d87e81c24495486ac53'
assets=[x for x in tree if x['type']=='blob' and x['path'].startswith('core/assets/') and Path(x['path']).suffix in ['.woff','.ttf','.frag','.vert']]
sources=['core/assets-raw/fontgen/config.json','core/src/mindustry/ui/Fonts.java','tools/src/mindustry/tools/IconConverter.java','core/src/mindustry/content/Planets.java','core/src/mindustry/graphics/g3d/PlanetRenderer.java','core/src/mindustry/graphics/g3d/MeshBuilder.java','core/src/mindustry/graphics/Shaders.java','core/src/mindustry/graphics/Drawf.java']
sources += [x['path']for x in tree if x['type']=='blob' and x['path'].startswith('core/src/mindustry/graphics/g3d/') and x['path'].endswith('Mesh.java')]
sources += ['core/src/mindustry/world/blocks/units/'+n+'.java'for n in ['UnitAssembler','UnitAssemblerModule','RepairTurret']]
def fetch(x):
    s=x['path'];p=HERE/'upstream'/s
    if p.exists():data=p.read_bytes()
    else:
        for attempt in range(5):
            try:data=urllib.request.urlopen('https://raw.githubusercontent.com/Anuken/Mindustry/'+COMMIT+'/'+s,timeout=40).read();break
            except Exception:
                if attempt==4:raise
                time.sleep(attempt+1)
        p.parent.mkdir(exist_ok=True,parents=True);p.write_bytes(data)
    assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==x['sha'],s
    return {'sourcePath':s,'sourceGitBlob':x['sha'],'file':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'disposition':'exact_upstream_technical_dependency' if x in assets else 'upstream_renderer_evidence','newArtwork':False,'runtimeIntegrationVerified':False}
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:rows=list(pool.map(fetch,assets+[by[p]for p in dict.fromkeys(sources)]))
result={'sourceCommit':COMMIT,'checkedAt':datetime.now(timezone.utc).isoformat(),'assets':[r for r in rows if r['disposition']=='exact_upstream_technical_dependency'],'rendererSources':[r for r in rows if r['disposition']=='upstream_renderer_evidence'],'status':'fetched_pending_semantic_review','note':'Font glyph metrics and shader programs are runtime dependencies. These are exact upstream reuse, not AI artwork.'}
HERE.mkdir(exist_ok=True);(HERE/'manifest.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'technicalAssets':len(result['assets']),'rendererSources':len(result['rendererSources'])}))
