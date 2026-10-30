import concurrent.futures, hashlib, io, json, struct, time, urllib.request
from pathlib import Path
from PIL import Image,ImageDraw

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
TREE=json.loads((ROOT/'records/reference-ui-sources/official-tree-v160.7.json').read_text(encoding='utf-8-sig'))
SHA='17012d61d9e4c3cbd9820d87e81c24495486ac53'
assets=json.loads((HERE.parent/'inventory-all-source-images.json').read_text())['assets']
paths=[x for x in assets if x['owner']=='ui-system']
source=HERE/'reference';source.mkdir(exist_ok=True)
def fetch(row):
    path=row['sourcePath'];out=source/path
    if not out.exists():
        request=urllib.request.Request('https://raw.githubusercontent.com/Anuken/Mindustry/'+SHA+'/'+path,
                                      headers={'User-Agent':'Mindustry-Art-Coverage'})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(request,timeout=45) as response:data=response.read()
                break
            except Exception:
                if attempt==3:raise
                time.sleep(attempt+1)
        actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        assert actual==row['sourceGitBlob'],path
        out.parent.mkdir(exist_ok=True,parents=True);out.write_bytes(data)
    data=out.read_bytes()
    r={**row,'localReference':out.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(data).hexdigest()}
    if out.suffix.lower() in ['.png','.jpg','.jpeg']:
        try:
            im=Image.open(io.BytesIO(data));r['sourceSize']=list(im.size);r['sourceMode']=im.mode
        except Exception as error:
            if data.startswith(b'\x89PNG\r\n\x1a\n'):
                r['sourceSize']=list(struct.unpack('>II',data[16:24]));r['sourceMode']='unknown'
                r['referenceDecodeError']=type(error).__name__
                r['dimensionEvidence']='PNG IHDR only; upstream Git blob bytes verified, replacement exported separately'
            else:raise
    return r
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(fetch,paths))
(HERE/'source-inventory.json').write_text(json.dumps({'schemaVersion':1,'referenceCommit':SHA,'assets':records},indent=2)+'\n',encoding='utf-8')
thumbs=[r for r in records if '/ui/sectors/' in r['sourcePath']]
plans=[]
for start in range(0,len(thumbs),9):
    group=thumbs[start:start+9];board=Image.new('RGB',(1536,1536),'#d4cbb8');d=ImageDraw.Draw(board)
    for i,row in enumerate(group):
        im=Image.open(ROOT/row['localReference']).convert('RGB');im=im.resize((440,440),Image.Resampling.NEAREST)
        col=i%3;line=i//3
        board.paste(im,(col*512+(512-im.width)//2,line*512+20))
        d.text((col*512+18,line*512+478),Path(row['sourcePath']).stem,fill='#222222')
    p=source/f'sector-guide-{start//9+1:02d}.png';board.save(p)
    plans.append({'batch':start//9+1,'grid':[3,3],'guide':p.relative_to(ROOT).as_posix(),'cells':group})
(HERE/'sector-batches.json').write_text(json.dumps(plans,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sourceCount':len(records),'sectorCount':len(thumbs),'sectorBatches':len(plans)}))
