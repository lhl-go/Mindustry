import concurrent.futures,hashlib,json,time,urllib.request
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parent
audit=json.loads((HERE/'audit.json').read_text(encoding='utf-8'));commit='17012d61d9e4c3cbd9820d87e81c24495486ac53'
def fetch(a):
    path=a['sourcePath'];out=HERE/'reference'/path;out.parent.mkdir(parents=True,exist_ok=True)
    for n in range(4):
        try:
            data=out.read_bytes()if out.exists()else urllib.request.urlopen(f'https://raw.githubusercontent.com/Anuken/Mindustry/{commit}/{path}',timeout=30).read()
            blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert blob==a['sourceGitBlob']
            if not out.exists():out.write_bytes(data)
            im=Image.open(out);im.load();a.update(localReference=out.relative_to(ROOT).as_posix(),sourceDimensions=list(im.size),sourceSha256=hashlib.sha256(data).hexdigest(),sourceAlphaBounds=list(im.convert('RGBA').getbbox()));return a
        except Exception as e:
            if n==3:return {**a,'referenceError':str(e)}
            time.sleep(1)
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as ex:
    assets=[]
    for i,a in enumerate(ex.map(fetch,audit['assets'])):
        assets.append(a)
        if i%50==49:print('Referenced '+str(i+1),flush=True)
report={'assets':assets,'errors':[a['sourcePath']for a in assets if 'referenceError'in a]}
(HERE/'source-inventory.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'count':len(assets),'errors':report['errors']}),flush=True)
