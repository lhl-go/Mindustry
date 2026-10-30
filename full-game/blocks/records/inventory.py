from pathlib import Path
import json,re,hashlib,collections,urllib.request,concurrent.futures,struct
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'full-game/blocks'
COMMIT='17012d61d9e4c3cbd9820d87e81c24495486ac53'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
s=(ROOT/'records/reference-unit-sources/Blocks.java').read_text(encoding='utf-8-sig')
tree=json.loads((ROOT/'records/reference-ui-sources/official-tree-v160.7.json').read_text(encoding='utf-8-sig'))
excluded={'environment':'terrain','props':'terrain','fire':'items-fx','extra':'root-ui'}
paths=[x for x in tree['tree'] if x['type']=='blob' and x['path'].startswith('core/assets-raw/sprites/blocks/') and x['path'].endswith('.png')]
matches=list(re.finditer(r'(?m)^\s{8}(\w+)\s*=\s*new\s+(\w+)\("([^"\n]+)"',s))
defs=[]
terrainclasses={'Floor','StaticWall','SteamVent','OreBlock','StaticProp','StaticTree','TallBlock','ShallowLiquid','TreeBlock','Prop','SeaBush','CharacterOverlay','RuneOverlay','OverlayFloor','AirBlock','SpawnBlock','RemoveWall','RemoveOre','Cliff','EmptyFloor','Seaweed','ColoredFloor','ColoredWall'}
for i,m in enumerate(matches):
 body=s[m.start():matches[i+1].start() if i+1<len(matches) else len(s)]
 sz=re.search(r'(?m)^            size = (\d+);',body)
 cat=re.search(r'requirements\(Category\.(\w+)',body)
 draws=sorted(set(re.findall(r'new (Draw\w+)',body)))
 cls=m.group(2)
 defs.append({'id':m.group(3),'javaName':m.group(1),'class':cls,'category':cat.group(1) if cat else None,'tileSize':int(sz.group(1)) if sz else 1,'source':{'file':'records/reference-unit-sources/Blocks.java','line':s[:m.start()].count('\n')+1,'commit':COMMIT},'drawerClasses':draws,'definition':body,'owner':'terrain' if cls in terrainclasses else 'blocks'})
known={d['id']:d for d in defs}
ids=sorted(known,key=len,reverse=True)
required=[]
for x in paths:
 cat=x['path'].split('/')[4]
 if cat in excluded:continue
 stem=Path(x['path']).stem
 candidates=[id for id in ids if stem==id or stem.startswith(id+'-') or re.fullmatch(re.escape(id)+r'\d+',stem)]
 id=candidates[0] if candidates else None
 suffix=stem[len(id):] if id else stem
 role='body' if not suffix else ('team-mask' if 'team' in suffix else 'heat-mask' if 'heat' in suffix or 'glow' in suffix else 'moving-part' if any(t in suffix for t in ['rotator','rotor','turbine','blade','top','barrel','pod','arm','spinner','thruster']) else 'layer-or-variant')
 required.append({'sourcePath':x['path'],'sourceGitBlob':x['sha'],'sourceBytes':x.get('size'),'blockId':id,'category':cat,'region':stem,'role':role,'sourceDimensions':None,'anchor':'center of original source canvas; native master mapping recorded per export','status':'required','output':None})
groups=collections.defaultdict(list)
for r in required:
 if r['blockId']:groups[r['blockId']].append(r['sourcePath'])
runtime=[]
blocks=[]
for d in defs:
 if d['owner']!='blocks':continue
 d['requiredSourcePaths']=groups[d['id']]
 d['runtimeDraws']=[x for x in d['drawerClasses'] if x in {'DrawFlame','DrawParticles','DrawArcSmelt','DrawBubbles','DrawCrucibleFlame','DrawLiquidTile','DrawLiquidRegion','DrawGlowRegion','DrawHeatRegion','DrawPulseShape'}]
 d['status']='required' if d['requiredSourcePaths'] else 'source_mapping_review'
 d['sizeAnchor']={'tileFootprint':[d['tileSize'],d['tileSize']],'worldUnitsPerTile':8,'sourcePixelsPerTile':32,'pivot':'canvas-center'}
 blocks.append(d)
write(OUT/'inventory.json',{'schema':'mindustry-full-game-blocks-inventory-v1','baseline':{'tag':'v160.7','commit':COMMIT},'scope':{'excludedDirectories':excluded,'requiredSourcePngCount':len(required),'blockCount':len(blocks)},'sourceFiles':required,'blocks':blocks,'unmatchedRegions':[x['region'] for x in required if not x['blockId']]})
write(OUT/'production-contract.json',{'baseline':COMMIT,'scope':'all artificial block sprite paths excluding environment/props/fire/extra','styleReferences':['designs/mail-ui-v1/01-mail-event.png','designs/team-ui-v2/team-ui-v2.png'],'camera':'orthographic top-down, north-up for directional machines','nativeArt':'builtin image_gen only; no code-drawn substitute','allowedDerivations':['alpha cleanup','native cell slicing','rotation','downscale to official canvas','source-derived animated motion','material/team/heat masks extracted from generated artwork'],'completion':'each required source path has explicit distinct artwork or documented compatible same-identity variant derivation; required moving layers separated; runtime draw operations mapped; visual and numeric QA; engine unverified until actually exercised','modelDisclosure':'target config snapshot; actual model and quality null when host does not disclose'})
print(json.dumps({'blocks':len(blocks),'requiredPngs':len(required),'unmatched':len([x for x in required if not x['blockId']]),'categories':dict(collections.Counter(x['category'] for x in required))},ensure_ascii=False))
if '--download' in __import__('sys').argv:
 def get(x):
  path=OUT/'reference-sprites'/x['sourcePath'].split('/sprites/')[1]
  path.parent.mkdir(parents=True,exist_ok=True)
  if not path.exists():
   for attempt in range(3):
    try:
     data=urllib.request.urlopen('https://raw.githubusercontent.com/Anuken/Mindustry/'+COMMIT+'/'+x['sourcePath'],timeout=30).read();path.write_bytes(data);break
    except Exception:
     if attempt==2:raise
  data=path.read_bytes();x['sourceDimensions']=list(struct.unpack('>II',data[16:24]));x['sourceSha256']=hashlib.sha256(data).hexdigest();return x
 with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
  for n,x in enumerate(ex.map(get,required),1):
   if n%100==0:print('Downloaded',n,flush=True)
 doc=json.loads((OUT/'inventory.json').read_text(encoding='utf-8'));doc['sourceFiles']=required
 write(OUT/'inventory.json',doc);print('Source dimensions complete',len(required))
