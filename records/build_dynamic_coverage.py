from pathlib import Path
import json,datetime,hashlib
root=Path(__file__).resolve().parents[1]
audit=json.loads((root/'records/dynamic-configuration-source-audit.json').read_text(encoding='utf-8'))
catalog=json.loads((root/'ui/preview/data.js').read_text(encoding='utf-8').removeprefix('window.ART_DATA=').strip().rstrip(';'))
groups={g['id']:g for g in catalog['groups']}
categories={'Accelerator':'星球发射选择 → UI-005','LandingPad':'物品格＋进口/出口来源选择','LaunchPad':'出口目的地选择 → UI-005','TargetDummy':'敌方/飞行复选框＋护甲/重置时间/尺寸','CanvasBlock':'编辑入口 → UI-027','LogicBlock':'编辑入口 → UI-024','MessageBlock':'多行消息编辑 → D-02','LightBlock':'颜色选择 → D-10','Constructor':'建筑配方格','PayloadRouter':'建筑与单位载荷选择','PayloadSource':'建筑与单位载荷来源','LiquidSource':'液体格','CoreBlock':'队伍选择及可用限制','Reconstructor':'单位默认指令选择','UnitFactory':'生产单位格＋默认指令选择'}
records=[]
for x in audit['builders']:
 name=x['path'].rsplit('/',1)[-1][:-5]
 if name=='ItemSelection':continue
 i=groups['UI-002']['requiredDesignStates'].index('动态配置：'+name)
 records.append(dict(className=name,source=x['path'],sourceSha256=x['sha256'],line=x['matches'][0]['line'],implementation='ui/preview/screen-variants.js#dynamicConfiguration',controls=categories.get(name,'可搜索物品选择格＋取消选择'),preview=f'ui/preview/index.html?id=UI-002&state={i}',png=f'ui/states/UI-002--s{i:02d}--desktop.png',mapped=True))
types=['图片','音效','音乐','文本','内容','补丁']
sourceclass=['MapImagesView','MapAudioView','MapAudioView','MapBundlesView','MapContentView','MapPatchesView']
maprows=[]
for kind,cl in zip(types,sourceclass):
 i=groups['UI-026']['requiredDesignStates'].index('资源类型：'+kind)
 p=root/'records/reference-dynamic-sources'/('core__src__mindustry__editor__data__'+cl+'.java')
 maprows.append(dict(type=kind,sourceClass=cl,sourceSha256=hashlib.sha256(p.read_bytes()).hexdigest(),preview=f'ui/preview/index.html?id=UI-026&state={i}',png=f'ui/states/UI-026--s{i:02d}--desktop.png',additionalReuse='UI-025 map translation editor' if kind=='文本' else 'D-11 file chooser; D-01 destructive confirmation'))
record=dict(checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),functionalCommit=audit['commit'],sourceFileCount=audit['scannedFileCount'],sourceScanErrors=audit['errors'],dynamicConfigurations=records,mapAssetTypes=maprows,gaps=[dict(id='GAP-01',status='art_mapping_closed',evidence='21 concrete configuration classes plus shared ItemSelection helper scanned and mapped individually'),dict(id='GAP-02',status='art_mapping_closed',evidence='6 asset categories, including separate sound/music modes of MapAudioView'),dict(id='GAP-03',status='browser_layout_checked_runtime_unverified',evidence='Desktop 1366x768 and mobile 844x390 layout checks; no Java/Android/iOS client was modified or run.')],notClaimed=['Complete game implementation','Server functionality','Real save/mod/ZIP operations','Engine atlas registration','Platform-native keyboard/dialog correctness'])
(root/'records/dynamic-coverage.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Dynamic configuration mappings',len(records),'map asset types',len(maprows))
