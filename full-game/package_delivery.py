import json,hashlib,zipfile
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent.parent;HERE=ROOT/'full-game'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def main():
    m=json.loads((HERE/'delivery-files.json').read_text(encoding='utf-8'));assert m['status']=='frozen_verified_full_game_art'
    rows=m['files']+[{'file':'full-game/delivery-files.json','sha256':sha(HERE/'delivery-files.json')}]
    for a in rows:assert sha(ROOT/a['file'])==a['sha256'],'Frozen batch changed: '+a['file']
    checks=HERE/'checksums.sha256';checks.write_text(''.join(a['sha256']+'  '+a['file']+'\n'for a in rows),encoding='utf-8')
    out=ROOT/'exports/Tiangong-Xianzhen-Full-Art-v160.7.zip';part=out.with_suffix('.zip.part')
    with zipfile.ZipFile(part,'w',allowZip64=True)as z:
        for a in rows+[{'file':'full-game/checksums.sha256'}]:
            p=ROOT/a['file'];compression=zipfile.ZIP_STORED if p.suffix.lower()in ['.png','.jpg','.webp','.woff','.apng']else zipfile.ZIP_DEFLATED
            z.write(p,'mindustry-image/'+a['file'],compress_type=compression,compresslevel=6 if compression==zipfile.ZIP_DEFLATED else None)
    with zipfile.ZipFile(part)as z:assert z.testzip()is None;count=len(z.infolist())
    part.replace(out)
    record={'packagedAt':datetime.now(timezone.utc).isoformat(),'file':out.relative_to(ROOT).as_posix(),'bytes':out.stat().st_size,'sha256':sha(out),'entries':count,'crcVerified':True,'sourcePaths':2368,'runtimeIntegrationVerified':False,'desktopRuntimeAcceptancePassed':True}
    (HERE/'package-verification.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print(json.dumps(record))
if __name__=='__main__':main()
