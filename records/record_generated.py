from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,hashlib,shutil,sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
receipt_path=ROOT/sys.argv[1]
receipt=json.loads(receipt_path.read_text(encoding='utf-8-sig'))
out=ROOT/receipt['targetFile'];out.parent.mkdir(parents=True,exist_ok=True)
source=Path(receipt['originalOutputPath'])
if not out.exists():shutil.copyfile(source,out)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(out)==sha(source)
args=receipt['submittedArguments'];prompt=ROOT/receipt['promptFile'];prompt.parent.mkdir(parents=True,exist_ok=True);prompt.write_text(args['prompt']+'\n',encoding='utf-8')
im=Image.open(out);im.verify();im=Image.open(out);im.load()
alpha=im.getchannel('A') if 'A' in im.getbands() else None
refs=[]
for p in args.get('referenced_image_paths',[]):
    pp=Path(p);refs.append(dict(path=str(pp),sha256=sha(pp),purpose='primary_style_reference' if pp.name in ('01-mail-event.png','team-ui-v2.png') else 'edit_target_or_secondary_reference',actuallySubmitted=True))
r=dict(schemaVersion=1,file=receipt['targetFile'],sha256=sha(out),width=im.width,height=im.height,format=im.format,mode=im.mode,
    nativeSize=[im.width,im.height],requestedSize=receipt['requestedSize'],resized=False,
    generatedAt=datetime.fromisoformat(receipt['returnedAt'].replace('Z','+00:00')).astimezone(ZoneInfo('America/New_York')).isoformat(),generatedAtBasis='tool_return_receipt',
    tool='image_gen.imagegen',route='builtin',configSnapshot=json.loads((ROOT.parent/'config/image-generation.json').read_text(encoding='utf-8-sig')),
    submittedParameters=dict(model=None,quality=None,size=None,**args),actualModel=None,actualQuality=None,
    unverifiedReason='Host-managed built-in tool provides no model/quality/size selectors or exact returned model/quality. Config and prompt are targets only.',
    prompt=receipt['promptFile'],promptSha256=sha(prompt),references=refs,
    evidence=dict(toolReceipt=str(receipt_path.relative_to(ROOT)),outputPath=str(source),nativePngSha256=sha(out),returnedKeys=receipt['resultMetadata']['keys']),
    alphaExtrema=alpha.getextrema() if alpha else None,alphaTransparentPixels=alpha.histogram()[0] if alpha else 0,status='generated_pending_review')
(out.with_name(out.name+'.generation.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:r[k] for k in ('file','width','height','mode','alphaExtrema','alphaTransparentPixels','sha256')},ensure_ascii=True))
