from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,re,shutil,sys,numpy as np
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[1];PROJ=ROOT.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ingest(stem):
 r=json.loads((BASE/'records'/f'{stem}.receipt.json').read_text(encoding='utf-8'));src=Path(re.search(r' as (C:.*?\.png) by default',r['result']['output_hint']).group(1));dst=BASE/'source'/f'{stem}.png';shutil.copyfile(src,dst)
 im=Image.open(dst);prompt=BASE/'prompts'/f'{stem}.txt';prompt.write_text(r['args']['prompt'],encoding='utf-8')
 rec=dict(file=dst.relative_to(ROOT).as_posix(),sha256=sha(dst),generatedAt=r['returnedAt'],startedAt=r['startedAt'],tool='image_gen.imagegen',route='builtin',width=im.width,height=im.height,format='PNG',mode=im.mode,configSnapshot=json.loads((PROJ/'config/image-generation.json').read_text(encoding='utf-8-sig')),submittedParameters=dict(model=None,quality=None,**r['args']),actualModel=None,actualQuality=None,unverifiedReason='Host managed, tool does not expose model/quality selectors or actual metadata.',prompt=prompt.relative_to(ROOT).as_posix(),references=[dict(file=p,sha256=sha(p),purpose='primary_style_reference',actuallyAttached=True) for p in r['args'].get('referenced_image_paths',[])],evidence=dict(receipt=(BASE/'records'/f'{stem}.receipt.json').relative_to(ROOT).as_posix(),originalOutputPath=str(src),fields=r['result']['keys']),names=r['names'],sourceImageRetained=True)
 write(dst.with_name(dst.name+'.generation.json'),rec);print(json.dumps({'stem':stem,'size':list(im.size)}))
def inventory():
 tree=json.loads((ROOT/'records/reference-ui-sources/official-tree-v160.7.json').read_text(encoding='utf-8-sig'));rows=[]
 for e in tree['tree']:
  p=e['path'];m=re.match(r'core/assets-raw/sprites/(items|effects|statuses|rubble|shapes|teams|blocks/fire)/(.+)\.png$',p)
  if m:rows.append(dict(id=m[2],group=m[1],officialPath=p,officialGitBlob=e['sha'],status='queued'))
 write(BASE/'inventory.json',dict(commit=tree['sha'],sourceTree='records/reference-ui-sources/official-tree-v160.7.json',sourcePathCount=len(rows),assets=rows,sourceState='actual_fixed_version_tree',runtimeVerification=False))
 print(json.dumps({'inventoryCount':len(rows)}))
if __name__=='__main__':
 if sys.argv[1]=='inventory':inventory()
 else:ingest(sys.argv[1])
