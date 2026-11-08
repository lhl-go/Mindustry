from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[1]
read=lambda f:json.loads((ROOT/f).read_text(encoding='utf-8-sig'))
def dump(f,d):(ROOT/f).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read('exports/manifest.json');v=read('records/final-delivery-verification.json');g=read('records/delivery-browser-qa.json');r=read('records/ui-render-all.json')
assert m['status']=='art_complete_runtime_unverified' and not m['validationErrors'] and v['passed'] and g['passed']
assert len(m['units'])==68 and len(m['ui'])==64 and sum(len(x['states']) for x in m['ui'])==308
assert len(r['records'])==616 and all(x['file'] and (ROOT/x['file']).is_file() and sha(ROOT/x['file'])==x['sha256'] for x in r['records'])
for src in r['sources']:assert sha(ROOT/src['file'])==src['sha256'],src['file']
spot=read('records/final-independent-ui-review.json');assert not spot['blockingFindings'] and spot['sampleCount']==8
for src in spot['images']:assert sha(ROOT/src['file'])==src['sha256'] and src['actuallyViewed']
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
summary=dict(acceptedAt=now,status='art_complete_runtime_unverified',version=m['version'],commit=m['commit'],unitArtMappings=68,unitLayersUnique=len({f for u in m['units'] for f in u['layers']}),unitPngFilesUnique=len({f for u in m['units'] for f in [u['file'],*u['layers']]}),uiGroups=64,stateFamilies=308,desktopStatePngs=308,mobileStatePngs=308,uiKitFiles=len(m['kit']),conceptPages=len(m['concepts']),characterCutouts=1,verifiedImageFiles=v['imageCount'],blockingArtIssues=[],physicalFileVerification='records/final-delivery-verification.json',uiVerification='records/ui-render-all.json',offlineGalleryVerification='records/delivery-browser-qa.json',deliveryEntry='exports/index.html',runtimeIntegrationVerified=False,unverifiedScope=['Mindustry atlas integration','in-game pivot registration and animated motion','actual-device touch geometry'],actualGenerationModel=None,actualGenerationQuality=None,modelEvidence='Host did not expose exact generation model or quality; individual records retain config targets and actual arguments separately.',sharedGitTouched=False)
exclusions=read('records/package-exclusions.json') if (ROOT/'records/package-exclusions.json').exists() else {'files':[]}
summary['localIntermediateImagesRetained']=len(exclusions['files']);summary['archiveOmitsRetainedIntermediates']=True;summary['cleanupLimitation']='Automatic approval rejected the prior 32-image cleanup with no detailed reason. No retry or alternative deletion of that list was performed.'
summary['independentVisualReview']='records/final-independent-ui-review.json'
dump('records/acceptance-summary.json',summary)
c=read('production-contract.json');c['status']=summary['status'];c['acceptedAt']=now;c['acceptanceSummary']='records/acceptance-summary.json';c['workflow']['initialBatchStatus']='resolved_see_records_first_batch_resolution';c['workflow']['nextSteps']=[];c['workflow']['artProductionStatus']='complete';dump('production-contract.json',c)
p=ROOT/'README.md';s=p.read_text(encoding='utf-8');s=s.replace('数量要求不等于完成数量，以台账实际记录为准。','全部 68 项单位美术及必要分层已完成；308 类界面状态各有桌面与移动横屏 PNG，共 616 张。验收计数见 [最终验收记录](records/acceptance-summary.json)。');s=s.replace('[UI 渲染记录](records/ui-render-screen.json)','[最终全量 UI 渲染记录](records/ui-render-all.json)');p.write_text(s,encoding='utf-8')
p=ROOT/'exports/README.md';s=p.read_text(encoding='utf-8');s=s.replace('其余 68 项需要独立美术。','其余 68 项已交付独立美术及必要分层。308 类状态已导出桌面和移动横屏两套，共 616 张 PNG。');s+='\n最终验收见 [验收汇总](../records/acceptance-summary.json) 与 [全文件验证](../records/final-delivery-verification.json)。旧检查图片已被最终导出取代，历史文字记录保留；清理对应关系见 [清理记录](../records/superseded-ui-image-cleanup.json)。\n';p.write_text(s,encoding='utf-8')
if exclusions['files']:
 note='\n自动审批拦截了 32 张中间图的批量删除，未给出具体原因；没有绕过或重试该删除。本地保留这些文件，正式 ZIP 排除清单中的中间图，全部正式素材与来源文字保留。参见 [打包排除清单](../records/package-exclusions.json)。\n'
 p=ROOT/'exports/README.md';p.write_text(p.read_text(encoding='utf-8')+note,encoding='utf-8')
 p=ROOT/'README.md';p.write_text(p.read_text(encoding='utf-8')+'\n本地仍保留 32 张被自动审批拦截删除的中间图；未重试或绕过，该批图片已从正式 ZIP 排除。详见 [打包排除与保留记录](records/package-exclusions.json)。\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
