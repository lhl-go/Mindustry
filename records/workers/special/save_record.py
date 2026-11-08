import sys,json,hashlib,datetime,struct
from pathlib import Path
from PIL import Image
root=Path(r'D:\work\image\mindustry-image')
stem=sys.argv[1]
ui=root/'units/special/boards'/f'{stem}.png'
rp=root/'records/workers/special'/f'{stem}.tool-receipt.json'
receipt=json.loads(rp.read_text(encoding='utf-8'))
prompt_path=root/'prompts/special'/f'{stem}.txt'
config=json.loads((root.parent/'config/image-generation.json').read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with Image.open(ui) as im:
    im.verify()
with Image.open(ui) as im:
    size=im.size; mode=im.mode; fmt=im.format; meta=list(im.info); alpha=im.getchannel('A').getextrema() if 'A' in im.getbands() else None
refs=[{'path':'../'+Path(p).relative_to(root.parent).as_posix(),'absolutePath':p,'sha256':sha(Path(p)),'purpose':'primary_style_reference','inspectedBeforeSubmission':True} for p in receipt['submittedArguments']['referenced_image_paths']]
generated=datetime.datetime.fromisoformat(receipt['returnedAt'].replace('Z','+00:00')).astimezone(datetime.timezone(datetime.timedelta(hours=-4))).isoformat()
record={'schemaVersion':1,'file':ui.relative_to(root).as_posix(),'pathBase':'mindustry-image/','generatedAt':generated,'generatedAtBasis':'Tool receipt return time; server generation timestamp not disclosed','startedAt':receipt['startedAt'],'tool':'image_gen.imagegen','route':'builtin','toolCallId':None,'toolResultId':None,'outputArtifactStem':Path(receipt['originalOutputPath']).stem,'width':size[0],'height':size[1],'format':fmt,'mode':mode,'sha256':sha(ui),'byteLength':ui.stat().st_size,'pngVerified':True,'metadataKeys':meta,'alphaExtrema':alpha,'nativeSize':{'width':size[0],'height':size[1]},'requestedSize':{'width':int(sys.argv[2]),'height':int(sys.argv[3]),'submission':'prompt_only'},'requestedSizeAchieved':size==(int(sys.argv[2]),int(sys.argv[3])),'resized':False,'pixelPostprocessing':False,'status':'generated_pending_visual_review','configSnapshot':config,'userExplicitModel':'GPT Image 2.5','submittedParameters':{'model':None,'quality':None,'size':None,**receipt['submittedArguments']},'parameterLimitations':'内置工具无 model、quality、size 专用参数；尺寸只在 prompt 请求。','actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露精确型号和质量；未验证可确认具体版本或质量的来源元数据。','prompt':prompt_path.relative_to(root).as_posix(),'promptSha256':sha(prompt_path),'references':refs,'evidence':{'toolReceipt':rp.relative_to(root).as_posix(),'returnedFields':receipt['resultMetadata']['returnedKeys'],'originalOutputPath':receipt['originalOutputPath'],'originalOutputSha256':sha(Path(receipt['originalOutputPath'])),'projectBytesMatchOriginal':sha(ui)==sha(Path(receipt['originalOutputPath']))},'integrationStatus':'not_runtime_integrated','functionalVersion':'v160.7','functionalCommit':'17012d61d9e4c3cbd9820d87e81c24495486ac53'}
ui.with_name(ui.name+'.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(ui),'size':size,'mode':mode,'sha256':record['sha256'],'alpha':alpha},ensure_ascii=False))

