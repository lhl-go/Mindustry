from pathlib import Path
import json,re,hashlib,datetime,collections
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
tree=json.loads((ROOT/'records/reference-ui-sources/official-tree-v160.7.json').read_text(encoding='utf-8-sig'))
source=(ROOT/'records/reference-unit-sources/Blocks.java').read_text(encoding='utf-8')
defs=[]
for m in re.finditer(r'(\w+)\s*=\s*new\s+(\w+)\("([^"\n]+)"(?:,\s*(\d+))?',source):
 start=m.start();stop=source.find('\n        ',m.end());body=source[m.end():source.find('\n        };',m.end())+11] if source[m.end():].lstrip().startswith('){{') else ''
 # Brace pairs are parsed independently of semicolons in anonymous initializers.
 suffix=source[m.end():];brace=suffix.find('{{')
 if brace>=0 and brace<12:
  end=suffix.find('}};');body=suffix[:end+3]
 else:body=suffix[:suffix.find(';')+1]
 props={k:v.strip() for k,v in re.findall(r'\b(variants|autotile|autotileVariants|autotileMidVariants|tilingVariants|blendGroup|parent|isLiquid|wallOre|drawEdgeIn|drawEdgeOut|clipSize|size|rotations)\s*=\s*([^;]+);',body)}
 cls=m.group(2);v=int(m.group(4)) if m.group(4) else (3 if cls in ['Floor','OverlayFloor','OreBlock'] else 2 if cls=='StaticWall' else None)
 if props.get('variants','').isdigit():v=int(props['variants'])
 defs.append({'variable':m.group(1),'class':cls,'name':m.group(3),'variants':v,'properties':props,'sourceLine':source[:start].count('\n')+1})
extra={'caustics.png','clouds.png','distortAlpha.png','fog.png','noise.png','noiseAlpha.png','rays.png','space.png'}
entries=[]
for t in tree['tree']:
 p=t['path']
 if t['type']!='blob' or not p.lower().endswith('.png'):continue
 if not ('sprites/blocks/environment/' in p or 'sprites/blocks/props/' in p or p.startswith('core/assets/cubemaps/stars/') or p.startswith('core/assets/sprites/planets/') or (p.startswith('core/assets/sprites/') and Path(p).name in extra)):continue
 stem=Path(p).stem;matches=[d for d in defs if stem==d['name'] or re.match(re.escape(d['name'])+r'(?:\d|[-])',stem)];d=max(matches,key=lambda x:len(x['name'])) if matches else None
 cat='natural_prop' if '/props/' in p else 'skybox' if '/cubemaps/' in p else 'planet_map' if '/planets/' in p else 'technical_texture' if Path(p).name in extra and '/environment/' not in p else 'normal_map' if 'normal' in stem else 'cliff_mask' if stem.startswith('cliff') else 'edge_mask' if 'stencil' in stem or stem in ['edge','edges'] else 'ore_overlay' if stem.startswith('ore-') else 'liquid_floor' if d and (d['properties'].get('isLiquid')=='true' or d['class']=='ShallowLiquid') else 'natural_wall' if 'wall' in stem or d and d['class'] in ['StaticWall','TiledWall'] else 'floor'
 entries.append({'officialPath':p,'region':stem,'gitBlobSha1':t['sha'],'officialByteCount':t.get('size'),'category':cat,'definition':d,'status':'pending','originalSize':None,'plannedArtSource':'existing_technical' if cat in ['normal_map','cliff_mask','edge_mask','technical_texture'] else 'host_image','runtimeIntegrationVerified':False})
result={'schemaVersion':1,'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceCommit':'17012d61d9e4c3cbd9820d87e81c24495486ac53','sourceTreeFile':'records/reference-ui-sources/official-tree-v160.7.json','sourceTreeSha256':hashlib.sha256((ROOT/'records/reference-ui-sources/official-tree-v160.7.json').read_bytes()).hexdigest(),'scopeCount':len(entries),'categoryCounts':dict(collections.Counter(e['category'] for e in entries)),'entries':entries,'definitions':[d for d in defs if any(e['definition'] and e['definition']['name']==d['name'] for e in entries)],'runtimeIntegrationVerified':False}
(HERE/'inventory.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'count':len(entries),'categories':result['categoryCounts'],'unmatched':sum(e['definition'] is None for e in entries)},ensure_ascii=False))
