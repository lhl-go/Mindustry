import json, hashlib, datetime
from pathlib import Path
from PIL import Image
root=Path(r'D:\work\image\mindustry-image')
work=root/'records/workers/menu-network-research'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
descs=[
('01-main-menu-v1','UI-001','主菜单与游戏子菜单','core/src/mindustry/ui/fragments/MenuFragment.java',
 ['桌面主菜单','开始游戏子菜单展开'],
 ['移动端菜单','资料库子菜单与平台条件入口'],
 ['六项主导航及四项游戏入口文字清楚，当前选中态明确。','背景保持工厂、运输、炼器与塔防辨识度；画面无旧项目游戏名。']),
('02-network-join-v1','UI-007','联机服务器列表与添加地址弹窗','core/src/mindustry/ui/dialogs/JoinDialog.java',
 ['局域网／已保存／社区列表','玩家名称','搜索与延迟排序','添加地址弹窗'],
 ['发现中／空列表','版本不兼容','连接／重连','编辑地址状态'],
 ['三组服务器行、人数延迟、收藏与编辑删除图标可辨。','192.0.2.10:6567 地址完整，取消和确定操作区分，弹窗层级清楚。']),
('03-research-tree-v1','UI-006','科技树与节点详情','core/src/mindustry/ui/dialogs/ResearchDialog.java',
 ['研究树选择入口','已解锁／可研究／条件未满足','研究进度','节点详情展开'],
 ['资源不足样例','切换研究树展开','缩放平移交互'],
 ['样例依赖与 SerpuloTechTree.java 中已核对分支相符。','中文节点名称、连接线、选中分类器详情和资源需求清楚。','研究数量为演示，不声称是官方实际费用。']),
('04-campaign-planet-v1','UI-005','战役星球与区块选择','core/src/mindustry/ui/dialogs/PlanetDialog.java',
 ['星球选择','可发射／锁定／已占领／受袭','发射来源选择入口','全局概览入口'],
 ['已占领区块继续／进入','详细生产／进出口／存储统计','改名／图标／放弃区块弹窗'],
 ['球面六边形区块、四种状态和 172→175 发射路线明确。','Serpulo/Erekir、资源和发射来源中文数字可读。']),
('05-map-editor-v1','UI-018','地图编辑工作台','core/src/mindustry/editor/MapEditorDialog.java',
 ['画笔选中','网格启用','撤销可用／重做禁用','画笔大小','显示建筑／地形／地表','旋转','未保存'],
 ['菜单展开','编辑器测试前后','其他工具子模式与选择态'],
 ['画布、工具、方块分类和材质网格层级清楚。','地表选中时仅显示地表纹理，避免类别与内容混淆。','地图名星号和未保存状态、画笔与网格选中态可读。'])
]
assets=[]
for stem, uiid, title, source, states, remaining, observations in descs:
    png=root/'ui/menu-network-research'/f'{stem}.png'
    recpath=png.with_name(png.name+'.generation.json')
    rec=json.loads(recpath.read_text(encoding='utf-8'))
    receipt=json.loads((work/f'{stem}.tool-receipt.json').read_text(encoding='utf-8'))
    prompt=root/rec['prompt']
    prompt.write_text(receipt['submittedArguments']['prompt'],encoding='utf-8')
    rec['promptSha256']=sha(prompt)
    for ref in rec['references']:
        ref['path']='../'+Path(ref['absolutePath']).relative_to(root.parent).as_posix()
        assert sha(Path(ref['absolutePath']))==ref['sha256']
    assert sha(png)==rec['sha256']
    with Image.open(png) as im:
        im.verify()
    rec['status']='static_concept_visual_reviewed'
    rec['functionalSources']=[{'path':source,'url':'https://github.com/Anuken/Mindustry/blob/v160.7/'+source}]
    if uiid=='UI-006':
        rec['functionalSources'].append({'path':'core/src/mindustry/content/SerpuloTechTree.java','localEvidence':'records/reference-unit-sources/SerpuloTechTree.java'})
    rec['visualReview']={'result':'passed_for_static_concept','inspectedUsing':'tool returned full image preview','observations':observations,'blockingVisualIssues':[],'runtimeAcceptance':False}
    recpath.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    assets.append({'uiId':uiid,'title':title,'file':png.relative_to(root).as_posix(),'generationRecord':recpath.relative_to(root).as_posix(),'prompt':rec['prompt'],'toolReceipt':str((work/f'{stem}.tool-receipt.json').relative_to(root)).replace('\\','/'),'sha256':rec['sha256'],'nativeSize':rec['nativeSize'],'requestedSize':{'width':2560,'height':1440},'requestedSizeAchieved':False,'resized':False,'staticConceptState':'visual_reviewed','coveredConceptStates':states,'remainingStatesForCoordinator':remaining,'visualReview':rec['visualReview'],'runtimeIntegrated':False,'sliceExported':False,'actualModel':None,'actualQuality':None})
manifest={'schemaVersion':1,'worker':'menu-network-research','updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'functionalVersion':'v160.7','functionalCommit':'17012d61d9e4c3cbd9820d87e81c24495486ac53','status':'five_static_concepts_complete_runtime_and_remaining_states_pending','assetCount':len(assets),'route':'builtin','modelTarget':'GPT Image 2.5 / config gpt-image-2.5-sunburst','qualityTarget':'max','actualModel':None,'actualQuality':None,'modelEvidenceLimit':'工具未披露，配置与提示词不等于已显式锁定实际型号或质量。','nativeResolutionNote':'全部实际输出1672×941；目标2560×1440未达到，未缩放或程序重绘。','integrationNote':'五张为静态整屏概念，动态文字、交互、控件切片与客户端运行验收不由此宣称完成。其余状态由协调者使用共用控件与原生文字构建。','assets':assets}
(work/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'assetCount':len(assets),'pngVerify':'passed','fileHashVerify':'passed','referenceHashVerify':'passed','manifest':str(work/'manifest.json')},ensure_ascii=False))
