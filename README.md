# 天工仙阵 · 全量游戏美术

已完成固定基线 **Mindustry v160.7** 的全量美术资源覆盖与静态检查，涵盖 **2368 个原版图片源路径**。离线双击 [全量美术目录](full-game/index.html) 可搜索、筛选和查看原生图、兼容图；[UI 与单位设计预览](exports/index.html) 保留完整布局与状态。

这是非官方美术资源包。基线为 [Anuken/Mindustry](https://github.com/Anuken/Mindustry) 的提交 `17012d61d9e4c3cbd9820d87e81c24495486ac53`。本包提供 Windows 桌面客户端的实际美术加载和渲染验收；渲染代码、字体字形、程序粒子和 3D 行星网格的保留方式有单独审计，不将这些技术复用说成重新绘制。

| 图片源类别 | 已覆盖路径 |
|---|---:|
| 平台图标、字体图形、UI 和战役图标 | 277 |
| 单位及其必要图层 | 290 |
| 建筑、生产、管线和运作部件 | 759 |
| 炮塔及其部件 | 145 |
| 地表、环境、墙体、矿物、装饰和天空 | 733 |
| 物品、液体、状态、弹体和特效纹理 | 164 |
| 合计 | 2368 |

同一原生素材可对应尺寸、对称、遮罩或状态派生；路径数量不等于新绘原画数量。各类别清单逐项区分新绘、派生和技术复用。6 个字体文件、41 个着色器、138 个字体符号和程序生成视觉的处理方式见 [运行时视觉审计](full-game/runtime-visuals/review.json)。这些保留项维持原版语义和渲染契约，并明确标记为复用。

既有 UI 交付包含 64 个制作组、308 类状态、616 张桌面和移动横屏图，以及 68 项独立单位身份。全量扩展补齐建筑、地形、物品、特效、系统图标和原版要求的单位图层。

## 使用

1. 打开 `full-game/index.html` 浏览美术；需要界面状态时打开 `exports/index.html`。
2. 查阅 [coverage.json](full-game/coverage.json)，其 `sourcePath` 是固定原版中的目标路径，`file` 是兼容输出，`nativeFile` 是可用的原生主图或派生基准。原生图实际尺寸记录在逐图元数据中；兼容图保持原版小画布，不能当作原生高清图。
3. 用 Python 执行 `python full-game/export_source_overlay.py --output <一个尚不存在的目录>`，生成经过哈希检查的源目录覆盖包。它不会改写现有游戏目录。再在固定版本的 Mindustry 源码工程中合入并运行原版资源构建流程。

界面大幅设计和离线状态预览属于接入设计资料。桌面 atlas 装载与代表性动态显示已增加实际游戏检查，具体依据和限制见 `full-game/integration/qa/runtime-acceptance.json`；移动设备和所有游戏流程仍未作穷尽运行验收。

## 风格与来源

沿用用户指定的道家 Q 版高清手绘风格：玉绿、象牙米白、暖金、圆润形体与细腻材质。当前制作规则、配置及两张主参考完整保存在 [project-instructions](full-game/project-instructions/README.md)。逐图记录区分目标型号/质量、实际提交参数、实际返回尺寸和派生步骤。

本批配置目标为 `gpt-image-2.5-sunburst / max`，采用内置 image_gen。工具未披露精确实际型号与质量，记录中保持未确认；裁切、缩放、遮罩和组合均不声称是新的模型生成或新增原生细节。本地像素清理与切片已经用户明确授权。

来源与许可见 [ATTRIBUTION.md](ATTRIBUTION.md)。覆盖清单、图像哈希、透明通道、原版画布、部件装配和重复地形检查均有记录；生成源板、参考原图与过时中间图不计入交付素材。此前被自动审批拒绝删除的 1249 张中间图已在用户随后明确授权后清理，来源文字记录保留；Logo 的 4 张过程图清理仍被审批拦截，已从交付包排除，详情见 [source-retention.json](full-game/source-retention.json)。

正式游戏名为 **天工仙阵**，公开仓库名沿用 `Mindustry`。透明 Logo 与逐图记录见 [品牌素材](branding/tiangong-xianzhen/README.md)，可直接加载的美术模块及游戏内验收见 [接入说明](full-game/integration/README.md)。
