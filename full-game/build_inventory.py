import collections, hashlib, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
source=ROOT/'records/reference-ui-sources/official-tree-v160.7.json'
tree=json.loads(source.read_text(encoding='utf-8-sig'))
assert not tree['truncated']
def owner(path):
    if path.startswith('core/assets-raw/sprites/blocks/props/'):return 'terrain'
    if path.startswith('core/assets-raw/sprites/blocks/fire/'):return 'items-fx'
    if path.startswith('core/assets-raw/sprites/blocks/extra/'):return 'ui-system'
    if path.startswith('core/assets-raw/sprites/blocks/environment/'):return 'terrain'
    if path.startswith('core/assets-raw/sprites/blocks/'):return 'blocks'
    if path.startswith('core/assets-raw/sprites/units/'):return 'units-existing-audit'
    if any(path.startswith('core/assets-raw/sprites/'+k+'/') for k in ['effects','items','rubble','shapes','statuses','teams']):return 'items-fx'
    if path.startswith('core/assets/cubemaps/') or path.startswith('core/assets/sprites/planets/'):return 'terrain'
    if path.startswith('core/assets/sprites/') and Path(path).name in ['caustics.png','clouds.png','distortAlpha.png','fog.png','noise.png','noiseAlpha.png','rays.png','space.png']:return 'terrain'
    return 'ui-system'
rows=[]
for x in tree['tree']:
    p=x['path']
    if x['type']=='blob' and p.lower().endswith(('.png','.jpg','.jpeg','.svg','.ico','.icns')):
        rows.append({'sourcePath':p,'sourceGitBlob':x['sha'],'sourceBytes':x.get('size'),
                     'owner':owner(p),'status':'requires_mapping','output':None,'disposition':None})
out={'schemaVersion':1,'referenceCommit':'17012d61d9e4c3cbd9820d87e81c24495486ac53',
     'treeSource':str(source.relative_to(ROOT)).replace('\\','/'),
     'treeSourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),
     'scope':'Every raster/vector/icon source file in the fixed upstream tree; runtime generated visuals require supplemental inventories.',
     'status':'in_progress','sourceImageCount':len(rows),'byOwner':dict(collections.Counter(x['owner'] for x in rows)),
     'assets':rows}
(HERE/'inventory-all-source-images.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='assets'},ensure_ascii=False))
