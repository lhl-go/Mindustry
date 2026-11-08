from pathlib import Path
from PIL import Image
import json,hashlib,shutil,re,sys
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(stem):
 receipt_path=HERE/(stem+'.receipt.json')
 receipt=json.loads(receipt_path.read_text(encoding='utf-8-sig'))
 match=re.search(r' as (C:.*?\.png) by default',receipt['result']['output_hint'])
 if not match:raise ValueError('No generated output path in tool receipt')
 source=Path(match.group(1));target=ROOT/'units/air-erekir-parts/source'/(stem+'.png')
 target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():raise FileExistsError(target)
 shutil.copyfile(source,target)
 with Image.open(target) as im:
  im.load();w,h=im.size;mode=im.mode;hist=im.getchannel('A').histogram() if 'A' in im.getbands() else None
 prompt=ROOT/'prompts/air-erekir-parts'/(stem+'.txt');prompt.parent.mkdir(parents=True,exist_ok=True)
 prompt.write_text(receipt['args']['prompt'],encoding='utf-8')
 record={
  'schemaVersion':1,'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),
  'generatedAt':receipt['returnedAt'],'generatedAtBasis':'tool_return_receipt_time','startedAt':receipt['startedAt'],
  'tool':'image_gen.imagegen','route':'builtin','width':w,'height':h,'format':'PNG','mode':mode,
  'requestedSize':receipt['requestedSize'],'resized':False,'configSnapshot':receipt['configSnapshot'],
  'submittedParameters':{'model':None,'quality':None,'size':None,**receipt['args']},
  'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理；内置工具无型号、质量或尺寸参数，工具回执未披露精确型号和质量。',
  'prompt':prompt.relative_to(ROOT).as_posix(),'promptSha256':sha(prompt),'references':receipt['references'],
  'evidence':{'receipt':receipt_path.relative_to(ROOT).as_posix(),'originalOutputPath':str(source),'originalOutputSha256':sha(source),'sourceBytesPreserved':sha(source)==sha(target),'returnedFields':receipt['result']['keys']},
  'regions':receipt['regions'],'status':'native_source_awaiting_slice_QA',
  'alphaInspection':{'present':hist is not None,'transparentPixels':hist[0] if hist else 0,'opaquePixels':hist[255] if hist else w*h,'partialPixels':sum(hist[1:255]) if hist else 0}
 }
 target.with_name(target.name+'.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'file':record['file'],'nativeSize':[w,h],'mode':mode,'sha256':record['sha256'],'alpha':record['alphaInspection']},ensure_ascii=False))
for stem in sys.argv[1:]:save(stem)
