"""Inspect original PNG bytes and save provenance; does not modify image pixels."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import Counter
import hashlib
import json
import struct
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
TZ = ZoneInfo('America/New_York')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def inspect(path):
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        image.load()
        width, height = image.size
        alpha = image.getchannel('A') if 'A' in image.getbands() else None
        hist = alpha.histogram() if alpha else None
        details = dict(width=width, height=height, format=image.format, mode=image.mode,
                       byteLength=path.stat().st_size, sha256=digest(path), pngVerified=True,
                       metadataKeys=list(image.info.keys()))
        if alpha:
            details['alpha'] = dict(extrema=alpha.getextrema(), nonzeroBounds=alpha.getbbox(),
                transparentPixels=hist[0], opaquePixels=hist[255],
                partialAlphaPixels=sum(hist[1:255]), transparentFraction=hist[0]/(width*height),
                mostCommonValues=sorted(enumerate(hist), key=lambda item:item[1], reverse=True)[:12],
                cornerValues=[alpha.getpixel(p) for p in [(0,0),(width-1,0),(0,height-1),(width-1,height-1)]])
        else:
            details['alpha'] = None
    data = path.read_bytes()
    chunks = []
    offset = 8
    while offset + 12 <= len(data):
        length = struct.unpack('>I', data[offset:offset+4])[0]
        chunk = data[offset+4:offset+8].decode('ascii')
        chunks.append(chunk)
        offset += length + 12
        if chunk == 'IEND':
            break
    details['pngChunks'] = chunks
    return details

config = json.loads((REPO/'config/image-generation.json').read_text(encoding='utf-8-sig'))
assets = [
    ('01-factory-defense-hud-v1', 'ui', (2560,1440), 'generated_concept_reviewed_with_notes'),
    ('02-alchemy-engineer-v1', 'characters', (2048,2048), 'selected_character_concept_edge_cleanup_pending'),
    ('02-alchemy-engineer-v2', 'characters', (2048,2048), 'rejected_no_edge_improvement'),
    ('02-alchemy-engineer-v3', 'characters', (2048,2048), 'rejected_no_edge_improvement'),
]
summary = []
for stem, folder, target, status in assets:
    path = ROOT/folder/(stem+'.png')
    if not path.exists():
        print('Skipped absent image:', path.name)
        continue
    receipt_path = ROOT/'records'/(stem+'.tool-receipt.json')
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    args = receipt['submittedArguments']
    prompt = ROOT/'prompts'/(stem+'.txt')
    prompt.write_text(args['prompt'] + '\n', encoding='utf-8')
    details = inspect(path)
    ref_entries = []
    for idx, ref in enumerate(args['referenced_image_paths']):
        ref_path = Path(ref)
        relative = ref_path.relative_to(REPO).as_posix()
        is_edit_target = folder == 'characters' and stem != '02-alchemy-engineer-v1' and idx == 0
        ref_entries.append(dict(path='../'+relative, absolutePath=str(ref_path),
            sha256=digest(ref_path), purpose='edit_target_identity_preservation' if is_edit_target
            else ('primary_style_reference' if 'mail-ui-v1' in relative or 'team-ui-v2/team-ui-v2' in relative else 'secondary_hud_material_reference'),
            inspectedBeforeSubmission=True))
    returned = datetime.fromisoformat(receipt['returnedAt'].replace('Z','+00:00'))
    record = dict(schemaVersion=1, file=path.relative_to(ROOT).as_posix(),
        pathBase='mindustry-image/', generatedAt=returned.astimezone(TZ).isoformat(),
        generatedAtBasis='Tool result receipt time; server generation timestamp not disclosed',
        startedAt=receipt['startedAt'], tool='image_gen.imagegen', route='builtin',
        toolCallId=None, toolResultId=None, outputArtifactStem=Path(receipt['originalOutputPath']).stem,
        **details, nativeSize=dict(width=details['width'],height=details['height']),
        requestedSize=dict(width=target[0],height=target[1], submission='prompt_only'),
        requestedSizeAchieved=(details['width'],details['height'])==target,
        resized=False, pixelPostprocessing=False, status=status,
        configSnapshot=config, userExplicitModel='GPT Image 2.5',
        submittedParameters=dict(model=None,quality=None,size=None,
            transparent_background=args['transparent_background'],
            referenced_image_paths=args['referenced_image_paths'],prompt=args['prompt']),
        parameterLimitations='内置接口只开放 prompt、参考图与 transparent_background；型号、质量、尺寸无专用参数。',
        actualModel=None,actualQuality=None,
        unverifiedReason='宿主管理，工具未披露／无可核实元数据。配置、提示词和官方公告不能证明实际返回型号或质量。',
        prompt=prompt.relative_to(ROOT).as_posix(),promptSha256=digest(prompt),references=ref_entries,
        evidence=dict(toolReceipt=receipt_path.relative_to(ROOT).as_posix(),
            returnedFields=receipt['resultMetadata']['returnedKeys'],
            originalOutputPath=receipt['originalOutputPath'],originalOutputSha256=digest(Path(receipt['originalOutputPath'])),
            projectBytesMatchOriginal=digest(Path(receipt['originalOutputPath']))==details['sha256'],
            embeddedModelMetadataFound=False,officialVerification='records/official-verification-20261026.json'))
    if folder=='characters' and stem!='02-alchemy-engineer-v1':
        record['editedFrom'] = dict(file='characters/02-alchemy-engineer-v1.png',
            sha256=digest(ROOT/'characters/02-alchemy-engineer-v1.png'),
            generationRecord='characters/02-alchemy-engineer-v1.png.generation.json')
    write_json(path.with_name(path.name+'.generation.json'),record)
    summary.append(dict(file=record['file'],status=status,**details))
write_json(ROOT/'records/pixel-inspection.json',dict(inspectedAt=datetime.now(TZ).isoformat(),images=summary))
print(json.dumps(summary,ensure_ascii=False,indent=2))
