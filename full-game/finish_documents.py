import json,collections
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent.parent;HERE=ROOT/'full-game'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def main():
    c=read(HERE/'coverage.json');assert c['status']=='all_source_images_verified'
    table='\n'.join('| '+name+' | '+str(c['domains'][key]['mapped'])+' |'for key,name in [('ui-system','平台图标、字体图形、UI 和战役图标'),('units','单位及其必要图层'),('blocks','建筑、生产、管线和运作部件'),('root-turrets','炮塔及其部件'),('terrain','地表、环境、墙体、矿物、装饰和天空'),('items-fx','物品、液体、状态、弹体和特效纹理')])
    text='''# Mindustry · 道家 Q 版全量美术

已完成固定基线 **Mindustry v160.7** 的全量美术资源覆盖与静态检查，涵盖 **2368 个原版图片源路径**。离线双击 [全量美术目录](full-game/index.html) 可搜索、筛选和查看原生图、兼容图；[UI 与单位设计预览](exports/index.html) 保留完整布局与状态。

这是非官方美术资源包。基线为 [Anuken/Mindustry](https://github.com/Anuken/Mindustry) 的提交 `17012d61d9e4c3cbd9820d87e81c24495486ac53`。本包没有宣称游戏客户端已运行验收，或所有渲染代码、字体字形、程序粒子和 3D 行星网格均已重绘。

| 图片源类别 | 已覆盖路径 |
|---|---:|
'''+table+'''
| 合计 | 2368 |

同一原生素材可对应尺寸、对称、遮罩或状态派生；路径数量不等于新绘原画数量。各类别清单逐项区分新绘、派生和技术复用。6 个字体文件、41 个着色器、138 个字体符号和程序生成视觉的处理方式见 [运行时视觉审计](full-game/runtime-visuals/review.json)。这些保留项维持原版语义和渲染契约，并明确标记为复用。

既有 UI 交付包含 64 个制作组、308 类状态、616 张桌面和移动横屏图，以及 68 项独立单位身份。全量扩展补齐建筑、地形、物品、特效、系统图标和原版要求的单位图层。

## 使用

1. 打开 `full-game/index.html` 浏览美术；需要界面状态时打开 `exports/index.html`。
2. 查阅 [coverage.json](full-game/coverage.json)，其 `sourcePath` 是固定原版中的目标路径，`file` 是兼容输出，`nativeFile` 是可用的原生主图或派生基准。原生图实际尺寸记录在逐图元数据中；兼容图保持原版小画布，不能当作原生高清图。
3. 用 Python 执行 `python full-game/export_source_overlay.py --output <一个尚不存在的目录>`，生成经过哈希检查的源目录覆盖包。它不会改写现有游戏目录。再在固定版本的 Mindustry 源码工程中合入并运行原版资源构建流程。

界面大幅设计和离线状态预览属于接入设计资料。atlas 装载、运动锚点、动态部件、队伍颜色、液体填充、程序特效及真实设备效果仍需在游戏里运行验收；静态检查不能替代这一步。

## 风格与来源

沿用用户指定的道家 Q 版高清手绘风格：玉绿、象牙米白、暖金、圆润形体与细腻材质。当前制作规则、配置及两张主参考完整保存在 [project-instructions](full-game/project-instructions/README.md)。逐图记录区分目标型号/质量、实际提交参数、实际返回尺寸和派生步骤。

本批配置目标为 `gpt-image-2.5-sunburst / max`，采用内置 image_gen。工具未披露精确实际型号与质量，记录中保持未确认；裁切、缩放、遮罩和组合均不声称是新的模型生成或新增原生细节。本地像素清理与切片已经用户明确授权。

来源与许可见 [ATTRIBUTION.md](ATTRIBUTION.md)。覆盖清单、图像哈希、透明通道、原版画布、部件装配和重复地形检查均有记录；生成源板、参考原图与过时中间图不计入交付素材。被自动审批拒绝删除的本地中间图没有重试删除，并从交付包排除，详情见 [source-retention.json](full-game/source-retention.json)。
'''
    (ROOT/'README.md').write_text(text,encoding='utf-8')
    attribution=(ROOT/'.work/github-publish/ATTRIBUTION.public.md').read_text(encoding='utf-8')
    attribution=attribution.replace('UI 与单位美术包','全量美术资源包').replace('- `records/reference-dynamic-sources/`','- `records/reference-dynamic-sources/`\n- `full-game/*/reference*`、`full-game/runtime-visuals/upstream/` 及逐图清单标记为技术复用的资源')
    attribution=attribution.replace('本包没有附带系统字体文件；UI 预览使用系统字体回退。','本包包含从固定上游版本原样保留的 6 个运行时字体文件，并记录它们的路径与哈希；这些不是新增 AI 字体。离线 HTML 预览仍使用系统字体回退。')
    attribution+='\n字体内部的作者、版权及许可字符串，以及 Fontello 各来源字体的声明，保存在 [字体来源说明](full-game/runtime-visuals/font-notices/README.md)。Noto Sans JP 与 Fira Code 的 OFL、ProggyCleanTT 的 MIT 声明随包附带；Darktech LDR 保留 Michał “Neoqueto” Nowak 的署名及其内嵌 [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) 许可链接。六个字体文件均未修改。这些字体许可不由本说明替换。\n'
    (ROOT/'ATTRIBUTION.md').write_text(attribution,encoding='utf-8')
    p=read(HERE/'production-contract.json');p['status']='art_complete_runtime_unverified';p['completedAt']=datetime.now(timezone.utc).isoformat();p['completionEvidence']=['full-game/coverage.json','full-game/runtime-visuals/review.json','full-game/qa/gallery-review.json'];p['publication']='New full-game batch prepared after all art checks. Publication receipt is recorded separately and is required before claiming GitHub completion.'
    (HERE/'production-contract.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'readme':'README.md','attribution':'ATTRIBUTION.md','status':p['status']}))
if __name__=='__main__':main()
