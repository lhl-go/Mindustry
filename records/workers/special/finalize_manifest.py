import json, hashlib, datetime
from pathlib import Path
import numpy as np
from PIL import Image

root = Path(r'D:\work\image\mindustry-image')
worker = root / 'records/workers/special'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
write = lambda p, data: p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
inventory = read(root / 'records/inventory-units.json')
index = {u['id']:u for u in inventory['units']}
extraction = read(worker / 'extraction.json')
expected = {'manifold','assembly-drone','dummy','renale','latum','anthicus-missile','quell-missile','disrupt-missile','scathe-missile','scathe-missile-phase','scathe-missile-surge','scathe-missile-surge-split'}
assert {u['id'] for u in extraction['assets']} == expected

def validate_image(rel, asset=False):
    p = root / rel
    rec = read(p.with_name(p.name+'.generation.json'))
    with Image.open(p) as im:
        assert im.format == 'PNG' and im.mode == 'RGBA', rel
        im.load()
        size = list(im.size)
        a = np.array(im)
    assert sha(p) == rec['sha256'], rel
    assert size == [rec['width'],rec['height']], rel
    for src in rec.get('derivedFrom',[]):
        assert sha(root/src['file']) == src['sha256'], src['file']
        assert (root/src['generationRecord']).exists()
    result = {'file':rel,'generationRecord':rel+'.generation.json','sha256':sha(p),'size':size,'mode':'RGBA','alphaExtrema':[int(a[:,:,3].min()),int(a[:,:,3].max())]}
    if asset:
        ys,xs = np.where(a[:,:,3]>0)
        bbox = [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
        pad = [bbox[0],bbox[1],size[0]-bbox[2],size[1]-bbox[3]]
        hidden = int(np.count_nonzero(np.any(a[:,:,:3]!=0,axis=2)&(a[:,:,3]==0)))
        assert min(pad)>=32 and hidden==0
        assert result['alphaExtrema'][0]==0 and result['alphaExtrema'][1]>=253
        result.update({'visibleBBox':bbox,'minimumTransparentPadding':min(pad),'nonzeroRgbInFullyTransparentPixels':hidden,'resampled':False})
    return result

boards = []
for p in sorted((root/'units/special/boards').glob('*.png')):
    rel = p.relative_to(root).as_posix()
    entry = validate_image(rel)
    rec = read(p.with_name(p.name+'.generation.json'))
    assert rec['actualModel'] is None and rec['actualQuality'] is None
    assert rec['submittedParameters']['model'] is None and rec['submittedParameters']['quality'] is None
    assert sha(root/rec['prompt']) == rec['promptSha256']
    receipt = read(root/rec['evidence']['toolReceipt'])
    assert (root/rec['prompt']).read_text(encoding='utf-8') == receipt['submittedArguments']['prompt']
    for ref in rec['references']:
        assert sha(Path(ref['absolutePath'])) == ref['sha256']
    entry.update({'prompt':rec['prompt'],'promptSha256':rec['promptSha256'],'toolReceipt':rec['evidence']['toolReceipt'],'requestedSize':rec['requestedSize'],'requestedSizeAchieved':False,'actualModel':None,'actualQuality':None})
    boards.append(entry)

observations = {
 'manifold':'货舱矿料、葫芦轮廓和双后引擎完整，深浅底没有明显杂色残边。',
 'assembly-drone':'钳、钻、扳手轮廓分明，机环内的透明孔保留，四周器具未被裁切。',
 'dummy':'同心标靶与三个发动机清楚，沙盒实体身份与普通战斗单位区分明确。',
 'renale':'3 段静态接合连续，六足主躯干、头部触角与尾尖完整。',
 'latum':'4 段静态接合连续，头角、紫红甲片与多足轮廓完整；与 Renale 有体型和配色差异。',
 'anthicus-missile':'狭长蓝晶尖、双翼与尾喷口完整，方向朝上。',
 'quell-missile':'短宽紫晶弹体和弧形翼完整，与 Anthicus 轮廓不同。',
 'disrupt-missile':'主体与独立双翼拼合连续，紫晶与尾喷口完整；翼铰点为美术估计。',
 'scathe-missile':'红晶重型弹体、短翼与单大喷口完整。',
 'scathe-missile-phase':'琥珀晶尖、六边形环与宽翼清楚，未烘焙护盾光圈。',
 'scathe-missile-surge':'黄晶、闪电纹与多段壳体清楚，保留 Scathe 家族外形。',
 'scathe-missile-surge-split':'子弹体更细短，黄晶与双小翼完整；本图只包含一个子弹体。'
}
assets = []
all_asset_files = set()
for u in extraction['assets']:
    entry = dict(u)
    entry.update(validate_image(u['file'],True))
    src = index[u['id']]
    entry.update({k:src.get(k) for k in ['officialNameZhCN','family','availability','artScope','parentWeaponOrEntity','definition']})
    entry['layerFiles'] = []
    for layer in u['layers']:
        entry['layerFiles'].append(validate_image(layer['file'],True))
        all_asset_files.add(layer['file'])
    all_asset_files.add(u['file'])
    qa = [validate_image(f"records/workers/special/qa/{u['id']}-{bg}.png") for bg in ['dark','light']]
    entry['visualReview'] = {'status':'passed_static_art_review','reviewer':'hud_review','method':'Pillow true alpha_composite on dark and light backgrounds, personally viewed with view_image','reviewedAt':now,'observations':[observations[u['id']]],'visibleBlockingIssues':[],'previews':qa}
    entry['status']='art_exported_runtime_pending'
    entry['runtimeVerified']=False
    assets.append(entry)

manifest = {
 'schemaVersion':1,'worker':'special','updatedAt':now,'functionalVersion':'v160.7','functionalCommit':'17012d61d9e4c3cbd9820d87e81c24495486ac53',
 'status':'twelve_special_unit_art_exports_complete_runtime_pending','assetCount':12,'generatedBoardCount':4,'independentUnitPngCount':12,'additionalLayerPngCount':10,
 'sourceInventory':'records/inventory-units.json','sourceInventorySha256':sha(root/'records/inventory-units.json'),
 'sourceReadForAttributes':['records/reference-unit-sources/UnitTypes.java','records/reference-unit-sources/Blocks.java','records/reference-unit-sources/UnitType.java','records/reference-unit-sources/MissileUnitType.java','records/reference-unit-sources/NeoplasmUnitType.java'],
 'modelTarget':'GPT Image 2.5 / config gpt-image-2.5-sunburst','qualityTarget':'max','actualModel':None,'actualQuality':None,
 'modelEvidenceLimit':'内置工具未披露实际型号和质量，也不提供显式型号／质量参数；目标配置不是实际返回的证明。',
 'nativeResolutionNote':'两张板实际 1774×887，两张板 1254×1254；提示中的 2048 目标未达到。全部独立图仅裁切、平移、加透明边与已有层合成，无放大或新绘制细节。',
 'processing':'用户已明确授权本地清理切片。采用 alpha>=16 连通部保留，清除全透明像素隐藏 RGB；按真实轮廓裁切并加 32px 透明边，未机械按格切图。',
 'boards':boards,'assets':assets,
 'excluded':[{'id':'block','reason':'官方内部方块映射代理，不设计独立角色或独立PNG。'}],
 'layerGuide':'units/special/README.md',
 'limitations':['未启动 Mindustry 客户端，未验证 atlas 名称、像素到世界尺度、旋转中心、装载、动画或战斗运行。','Renale/Latum 分段数量与尾到头顺序依 v160.7 源码；当前共有画布和重叠仅验证静态接合，摆动时接缝仍需运行验收。','Disrupt 双翼枢轴是美术估计；正式 RegionPart 位移、缩放、镜像与旋转需对照客户端验证。','Manifold 货物、装配工具随主体绘制；官方货物与建造状态动态覆盖、队伍着色、阴影及光效仍需客户端配置。','引擎、尾迹、护盾、爆炸与分裂等效果计划复用官方程序效果，未制作为本批静态位图或验证特效表现。'],
 'validation':{'exactAssigned12Ids':True,'uniqueUnitAndLayerPngs':len(all_asset_files),'allPngHeadersAndHashesMatch':True,'allGenerationAndDerivationRecordsPresent':True,'allReferenceAndPromptHashesMatch':True,'allAssetAlphaMeaningful':True,'allAssetTransparentPaddingAtLeast32Px':True,'allFullyTransparentRgbZero':True,'all12ViewedOnDarkAndLightBackgrounds':True,'runtimeIntegrationAccepted':False}
}
assert len(all_asset_files)==22
write(worker/'manifest.json',manifest)
write(worker/'verification.json',{'checkedAt':now,'result':'passed_files_pixels_provenance_and_static_visual_only','validation':manifest['validation'],'sourceBoardSizes':[b['size'] for b in boards],'assets':[{'id':a['id'],'file':a['file'],'sha256':a['sha256'],'size':a['size']} for a in assets]})
print(json.dumps({'assets':12,'layers':10,'boards':4,'manifest':'records/workers/special/manifest.json','checks':'passed','runtimeVerified':False}))
