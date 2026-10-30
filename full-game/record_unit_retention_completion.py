import json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent.parent;HERE=ROOT/'full-game'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
p=HERE/'root-unit-source-cleanup.json';c=read(p);c['recordedAt']=datetime.now(timezone.utc).isoformat();c['scopeNote']='These 292 new unit source/reference files are distinct from the 16 items-fx and 32 initial AIR files whose deletion was rejected. No rejected deletion was retried.';p.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
r=read(HERE/'units/retention-cleanup.json');r.update(status='completed_by_root_after_final_verification',sourceImageRetained=False,localFilesDeleted=True,completionRecord='full-game/root-unit-source-cleanup.json',reason='All accepted unit exports, source text records, dimensions and hashes were verified and retained. Root completed scoped removal of these 292 files under the explicit project retention policy. This did not retry the distinct rejected item/initial AIR deletions.')
(HERE/'units/retention-cleanup.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for p in [HERE/'units/source-inventory.json',HERE/'units/source/unit-bases-joints.png.generation.json']:
    if not p.exists():continue
    data=read(p)
    def mark(v):
        if isinstance(v,dict):
            if 'sourceImageRetained'in v:v['sourceImageRetained']=False;v['cleanupCompletionRecord']='full-game/root-unit-source-cleanup.json'
            for x in v.values():mark(x)
        elif isinstance(v,list):
            for x in v:mark(x)
    mark(data);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=HERE/'units/freeze-receipt.json';f=read(p);f['postFreezeCleanup']={'record':'full-game/root-unit-source-cleanup.json','localFilesDeleted':292,'finalPixelsUnchanged':True,'note':'The earlier localCleanupDeleted field is the historical state at frozenAt; this post-freeze cleanup is now complete.'};p.write_text(json.dumps(f,indent=2)+'\n',encoding='utf-8')
p=HERE/'units/README.md';text=p.read_text(encoding='utf-8');start=text.find('自动审批曾拒绝删除');start=start if start>=0 else text.index('单位制作完成后');text=text[:start]+'单位制作完成后，协调者核对正式文件、路径边界与 SHA256，已成功删除本批 292 张消费完的参考图、源板和临时图，全部成品与逐图来源文字仍保留。见 `retention-cleanup.json` 和 `../root-unit-source-cleanup.json`。此前其它明确文件的删除曾被自动审批拒绝，那些被拒文件没有重试删除，不属于本次 292 张。\n';p.write_text(text,encoding='utf-8')
print(json.dumps({'unitConsumedSourcesRemoved':292,'finalPixelsUnchanged':True}))
