import json,hashlib,datetime
from pathlib import Path
root=Path(r'D:\work\image\mindustry-image')
out=root/'records/workers/final-audit'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
browser=read(out/'screen-fixes-browser.json');interaction=read(out/'interaction-check.json')
source_files=['ui/preview/screen-audit-fixes.js','ui/preview/screen-audit-fixes.css','ui/preview/data.js','ui/preview/index.html','ui/preview/unit-art.js','ui/preview/unit-art-data.js','records/inventory-ui.json','records/dynamic-coverage.json']
manifest={
 'status':'ready_for_root_state_export',
 'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'worker':'hud_review',
 'affectedIds':browser['affectedIds'],
 'stateCount':browser['stateViewportPairs']//2,
 'stateViewportPairs':browser['stateViewportPairs'],
 'renderFailures':len(browser['failed']),
 'duplicateStates':browser['duplicateStates'],
 'consoleErrors':browser['errors'],
 'offlineCheck':browser['offlineCheck'],
 'interactionChecks':interaction['checks'],
 'visualReview':{'representativeScreenshotsViewed':16,'latestChatScreenshotRechecked':True,'result':'passed for listed screen layout scope','files':[p.relative_to(root).as_posix() for p in sorted((out/'screenshots').glob('*.png'))]},
 'sources':[{'file':f,'sha256':sha(root/f)} for f in source_files],
 'evidence':[{'file':p.relative_to(root).as_posix(),'sha256':sha(p)} for p in [out/'static-check.json',out/'screen-fixes-browser.json',out/'interaction-check.json']],
 'rootFollowup':['Re-export the affected UI states after final unit-art mappings settle.','Correct README sidecar wording for browser-rendered state PNGs.'],
 'runtimeIntegrationVerified':False,
 'otherFamilyProduction': 'Excluded from missing-art failure conclusions while actively in production.',
 'builderCompositeFix':'Root-reported Alpha/Beta/Gamma fix; this worker did not re-review the replacement composites.',
 'originalConceptNativeResolutionVerifiedByThisPass':False,
}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:manifest[k] for k in ['status','stateCount','stateViewportPairs','renderFailures','duplicateStates','consoleErrors']},ensure_ascii=False))
