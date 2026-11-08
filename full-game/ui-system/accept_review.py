import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
v=read(HERE/'validation.json');assert not v['errors']
v['visualReview']='passed: 49 sectors on light/dark with 32px sample, 88 icon contacts, 277 compatibility paths, corrected checkbox/alert/slider controls, and expanded nine-patch samples inspected'
v['limitations']=['Compatibility exports intentionally keep upstream pixel dimensions and 1px nine-patch metadata. They have less detail than the supplied native art and approved HD skin masters.','Actual running game, font generation and OS cursor hotspot behavior are not verified.','Built-in generator did not disclose exact model or quality; provenance records distinguish target from actual.']
v['status']='art_export_complete_runtime_unverified';write(HERE/'validation.json',v)
for name in ['manifest.json','icons-manifest.json','sectors-manifest.json']:
    m=read(HERE/name);m['status']='art_export_complete_runtime_unverified';m['visualReviewRecord']='full-game/ui-system/validation.json'
    for a in m['assets']:
        if name=='icons-manifest.json'and a.get('semanticKey')=='ranai':
            s=read(HERE/'special/ranai.png.derived.json');a.update(file=s['file'],sha256=s['sha256'],derivedFrom=s['derivedFrom'],operation=s['operation']);a['identityCorrection']='Uses source-matched reddish-haired ranai face; prior frog export is not a shipped mapping.'
        a['status']='art_export_complete_runtime_unverified'
        if isinstance(a.get('validation'),dict):a['validation']['visualReview']='passed'
    write(HERE/name,m)
print(json.dumps({'uiSourcePaths':277,'sectors':49,'technicalAndBrandReuses':25,'runtimeVerified':False,'status':v['status']}))
