import urllib.request,json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parent
tree=json.loads((ROOT/'records/reference-ui-sources/official-tree-v160.7.json').read_text())['tree'];by={a['path']:a for a in tree};commit='17012d61d9e4c3cbd9820d87e81c24495486ac53'
for p in ['core/src/mindustry/entities/part/RegionPart.java','core/src/mindustry/world/blocks/defense/turrets/ContinuousLiquidTurret.java','core/src/mindustry/world/blocks/defense/turrets/LiquidTurret.java','core/src/mindustry/world/draw/DrawTurret.java']:
 out=HERE/'reference'/Path(p).name
 data=out.read_bytes()if out.exists()else urllib.request.urlopen('https://raw.githubusercontent.com/Anuken/Mindustry/'+commit+'/'+p,timeout=30).read()
 assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==by[p]['sha'];out.write_bytes(data)
 print(Path(p).name,flush=True)
