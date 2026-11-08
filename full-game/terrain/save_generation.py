from pathlib import Path
from PIL import Image
import json,re,hashlib,shutil,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];REPO=ROOT.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for stem in sys.argv[1:]:
 receipt=HERE/'records'/(stem+'.receipt.json');r=json.loads(receipt.read_text(encoding='utf-8'))
 original=Path(re.search(r' as (C:.*?\.png) by default',r['result']['output_hint']).group(1));dest=HERE/'source'/(stem+'.png');dest.parent.mkdir(exist_ok=True)
 if not dest.exists():shutil.copyfile(original,dest)
 with Image.open(dest) as im:im.load();size=list(im.size);mode=im.mode
 prompt=HERE/'prompts'/(stem+'.txt');prompt.parent.mkdir(exist_ok=True);prompt.write_text(r['args']['prompt'],encoding='utf-8')
 rec={'schemaVersion':1,'file':dest.relative_to(ROOT).as_posix(),'sha256':sha(dest),'generatedAt':r['returnedAt'],'startedAt':r['startedAt'],'tool':'image_gen.imagegen','route':'builtin','art_source':'host_image','width':size[0],'height':size[1],'format':'PNG','mode':mode,'requestedSize':r['requestedSize'],'resized':False,'configSnapshot':json.loads((REPO/'config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'size':None,**r['args']},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具无型号/质量/尺寸选择器，回执未披露实际型号或质量。','prompt':prompt.relative_to(ROOT).as_posix(),'promptSha256':sha(prompt),'references':[{'file':p,'sha256':sha(p),'purpose':'primary approved Daoist Q style only','personallyViewed':True} for p in r['args']['referenced_image_paths']],'evidence':{'receipt':receipt.relative_to(ROOT).as_posix(),'originalOutput':str(original),'originalOutputSha256':sha(original)},'regions':r['regions'],'status':'generated_native_awaiting_export'}
 dest.with_name(dest.name+'.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'stem':stem,'nativeSize':size,'mode':mode,'regions':len(r['regions'])},ensure_ascii=False))
