from pathlib import Path
import json,hashlib,datetime
H=Path(__file__).resolve().parent;R=H.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
m=json.loads((H/'manifest.json').read_text(encoding='utf8'))
keep_geometry={a['officialPath'] for a in m['assets'] if a['artSource']=='host_image_material_with_official_geometry'}
files=[]
for p in list((H/'source').glob('*.png'))+list((H/'reference').rglob('*.png')):
 if p.is_relative_to(H/'reference') and p.relative_to(H/'reference').as_posix() in keep_geometry:continue
 files.append({'file':p.relative_to(R).as_posix(),'absolutePath':str(p.resolve()),'sha256':sha(p),'excludeFromDeliveryArchive':True,'reason':'Consumed generation board or upstream visual reference; final native and engine PNGs plus complete textual provenance retained.'})
assert len(files)==713,len(files)
write(H/'retention-cleanup.json',{'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'planned_after_visual_and_hash_acceptance','scope':'Only full-game/terrain/source/*.png and full-game/terrain/reference/**/*.png excluding45necessary geometry inputs','files':files,'retainedSourceGeometryCount':45,'retainedFinalNativePanorama':'full-game/terrain/native/stars-equirectangular.png','outsideScopeUntouched':True})
p=H/'native/stars-equirectangular.png';m['nativeMasters']=[{'file':p.relative_to(R).as_posix(),'sha256':sha(p),'record':p.relative_to(R).as_posix()+'.derived.json','size':[1774,887],'role':'Final native-resolution seamless star panorama; input required to regenerate all six cube faces without independent generation or fake detail.'}]
# Explicit necessary hybrid geometry input list allows coordinator to include it if rebuilding is required.
m['integrationGeometryInputs']=[{'officialPath':p,'file':'full-game/terrain/reference/'+p,'sha256':sha(H/'reference'/p),'role':'GPL upstream alpha and structural shade required for faithful hybrid autotile rebuild'} for p in sorted(keep_geometry)]
write(H/'manifest.json',m);print(json.dumps({'plannedConsumedImages':len(files),'requiredGeometryInputs':len(keep_geometry)}))
