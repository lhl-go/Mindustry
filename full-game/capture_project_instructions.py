import json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent.parent;SOURCE=ROOT.parent;OUT=ROOT/'full-game/project-instructions'
paths=['AGENTS.md','config/image-generation.json','docs/IMAGE_MODEL_POLICY.md','docs/GIT_LATEST_STATE_POLICY.md','designs/mail-ui-v1/01-mail-event.png','designs/team-ui-v2/team-ui-v2.png']
rows=[]
for rel in paths:
    p=SOURCE/rel;assert p.is_file(),p;dest=OUT/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
    digest=hashlib.sha256(p.read_bytes()).hexdigest();assert hashlib.sha256(dest.read_bytes()).hexdigest()==digest
    rows.append({'sourceProjectRelativePath':rel,'file':dest.relative_to(ROOT).as_posix(),'sha256':digest})
(OUT/'README.md').write_text('# 原制作项目的当前规则与风格参考\n\n这里保存 image 制作项目的 AGENTS.md、模型策略和两张指定风格参考的当前字节副本。路径关系在本目录内保持；涉及原项目地图、并行坐标和其它游戏客户端的文件不属于 Mindustry 美术交付范围。此副本不表示那些外部项目也已完成或发布。\n\n每张素材自己的生成记录保留当时读取的配置与实际工具证据。当前规则副本不会改写旧图型号记录。\n',encoding='utf-8')
(OUT/'capture.json').write_text(json.dumps({'capturedAt':datetime.now(timezone.utc).isoformat(),'files':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'captured':len(rows),'sha256':rows[0]['sha256']}))
