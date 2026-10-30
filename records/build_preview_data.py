from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
ui=json.loads((ROOT/'records/inventory-ui.json').read_text(encoding='utf-8-sig'))
units=json.loads((ROOT/'records/inventory-units.json').read_text(encoding='utf-8-sig'))
groups=[]
for key,kind in [('screens','screen'),('reusableDialogs','dialog'),('sharedComponents','component')]:
    for row in ui[key]:groups.append(dict(row,requiredDesignStates=list(row['requiredDesignStates']),kind=kind))
audit=json.loads((ROOT/'records/dynamic-configuration-source-audit.json').read_text(encoding='utf-8'))
configs=[x['path'].rsplit('/',1)[-1][:-5] for x in audit['builders'] if not x['path'].endswith('/ItemSelection.java')]
next(g for g in groups if g['id']=='UI-002')['requiredDesignStates'] += ['动态配置：'+x for x in configs]
next(g for g in groups if g['id']=='UI-026')['requiredDesignStates'] += ['资源类型：'+x for x in ['图片','音效','音乐','文本','内容','补丁']]
data=dict(version='v160.7',groups=groups,units=[dict(id=u['id'],name=u.get('officialNameZhCN') or u['id'],group=u['group'],family=u['family'],artRequired=u['independentArtRequired']) for u in units['units']])
(ROOT/'ui/preview/data.js').write_text('window.ART_DATA='+json.dumps(data,ensure_ascii=False)+';\n',encoding='utf-8')
print('Catalog groups',len(groups),'required state families',sum(len(g['requiredDesignStates']) for g in groups))
