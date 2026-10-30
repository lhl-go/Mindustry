"""Keep tool receipt evidence without duplicating consumed source-board pixels in JSON."""
import json,hashlib,base64,re
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent.parent;HERE=ROOT/'full-game'
sha=lambda b:hashlib.sha256(b).hexdigest()
rows=[]
for p in (HERE/'blocks/records').glob('*.receipt.json'):
    before=p.read_bytes();receipt=json.loads(before);value=receipt.get('image_url')
    if not isinstance(value,str)or not value.startswith('data:image/'):continue
    header,encoded=value.split(',',1);assert ';base64'in header
    raw=base64.b64decode(encoded,validate=True);hint=receipt.get('output_hint','')
    source=Path(re.search(r' as (.+\.png) by default',hint).group(1))
    assert source.is_file()and sha(source.read_bytes())==sha(raw),'Original generated source unavailable/different: '+p.name
    receipt.pop('image_url');receipt['imagePayload']={'omitted':True,'reason':'Final package retains native extracts and source-image digest, not a second base64 copy of the consumed generation board.','mimeType':header.split(';')[0][5:],'bytes':len(raw),'sha256':sha(raw),'sourceFileVerified':str(source)}
    p.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    rows.append({'file':p.relative_to(ROOT).as_posix(),'beforeSha256':sha(before),'afterSha256':sha(p.read_bytes()),'sourceImageSha256':sha(raw),'sourceImageBytes':len(raw),'sourcePngDeleted':False})
out=HERE/'block-receipt-compaction.json'
if rows:
    out.write_text(json.dumps({'recordedAt':datetime.now(timezone.utc).isoformat(),'operation':'Remove redundant inline image payload from tool JSON receipts, preserving source hashes and all disclosed result metadata. Source PNGs were not deleted by this script.','files':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'compactedReceipts':len(rows),'sourcePngDeleted':False}))
