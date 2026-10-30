from pathlib import Path
import urllib.request,json,hashlib
here=Path(__file__).resolve().parent;commit='17012d61d9e4c3cbd9820d87e81c24495486ac53';results=[]
for name in ['core/src/mindustry/content/Planets.java','core/src/mindustry/graphics/g3d/PlanetRenderer.java','core/src/mindustry/graphics/CacheLayer.java','core/src/mindustry/graphics/FloorRenderer.java','core/src/mindustry/graphics/Shaders.java']:
 p=here/'source-code'/name;p.parent.mkdir(parents=True,exist_ok=True)
 try:
  if not p.exists():p.write_bytes(urllib.request.urlopen('https://raw.githubusercontent.com/Anuken/Mindustry/'+commit+'/'+name,timeout=20).read())
  results.append({'path':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sourceCommit':commit})
 except Exception as e:results.append({'path':name,'error':str(e)})
(here/'records/code-fetch.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8');print(json.dumps(results))
