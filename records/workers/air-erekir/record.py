from pathlib import Path
from datetime import datetime
import json,hashlib,shutil,re,sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
for stem in sys.argv[1:]:
    receipt_path=HERE/(stem+'.receipt.json')
    receipt=json.loads(receipt_path.read_text(encoding='utf-8-sig'))
    found=re.search(r' as (C:.*?\.png) by default',receipt['result']['output_hint'])
    source=Path(found.group(1))
    target=ROOT/'units/air-erekir/source'/(stem+'.png')
    target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists(): shutil.copyfile(source,target)
    with Image.open(target) as im:
        im.load(); w,h=im.size; mode=im.mode; hist=im.getchannel('A').histogram() if 'A' in im.getbands() else None
    prompt=ROOT/'prompts/air-erekir'/(stem+'.txt')
    if not prompt.exists():prompt.write_text(receipt['args']['prompt']+'\n',encoding='utf-8')
    refs=[dict(path=str(Path(p)),sha256=sha(Path(p)),purpose='edit_target' if '/units/' in p.replace('\\','/') else 'primary_style_reference',inspected=True) for p in receipt['args']['referenced_image_paths']]
    record=dict(schemaVersion=1,file=target.relative_to(ROOT).as_posix(),sha256=sha(target),generatedAt=receipt['returnedAt'],generatedAtBasis='tool_return_receipt_time',startedAt=receipt['startedAt'],tool='image_gen.imagegen',route='builtin',width=w,height=h,format='PNG',mode=mode,requestedSize=[receipt['requestedWidth'],receipt['requestedHeight']],resized=False,
        configSnapshot=json.loads((ROOT.parent/'config/image-generation.json').read_text(encoding='utf-8-sig')),
        submittedParameters=dict(model=None,quality=None,size=None,**receipt['args']),actualModel=None,actualQuality=None,
        unverifiedReason='宿主管理；内置工具无型号、质量或尺寸参数，返回未披露精确型号和质量。',
        prompt=prompt.relative_to(ROOT).as_posix(),promptSha256=sha(prompt),references=refs,
        evidence=dict(receipt=receipt_path.relative_to(ROOT).as_posix(),originalOutputPath=str(source),originalOutputSha256=sha(source),sourceBytesPreserved=sha(source)==sha(target),returnedFields=receipt['result']['keys']),
        alphaInspection=dict(present=hist is not None,transparentPixels=hist[0] if hist else 0,opaquePixels=hist[255] if hist else w*h,partialPixels=sum(hist[1:255]) if hist else 0),units=receipt['units'],status='native_source_current_design')
    target.with_name(target.name+'.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(stem=stem,size=[w,h],mode=mode,alpha=record['alphaInspection']),ensure_ascii=False))
