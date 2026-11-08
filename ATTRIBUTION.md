# 来源与许可说明

本仓库是由 **lhl-go** 发布的非官方道家 Q 版 全量美术资源包，与 Mindustry 官方项目独立维护。

原项目为 **Anuken 与 Mindustry 贡献者**开发的 [Mindustry](https://github.com/Anuken/Mindustry)。本次界面功能、单位身份、武器及部件映射以 [v160.7](https://github.com/Anuken/Mindustry/releases/tag/v160.7) 为基线，固定提交为 [`17012d61d9e4c3cbd9820d87e81c24495486ac53`](https://github.com/Anuken/Mindustry/tree/17012d61d9e4c3cbd9820d87e81c24495486ac53)。项目名称及官方单位标识用于说明对应关系，不表示官方授权或背书。

以下目录保存从该版本取得的参考源码、界面文案或许可证，用于核对美术覆盖和资源映射：

- `records/reference-ui-sources/`
- `records/reference-unit-sources/`
- `records/reference-dynamic-sources/`
- `full-game/*/reference*`、`full-game/runtime-visuals/upstream/` 及逐图清单标记为技术复用的资源

这些上游文件保留其原有版权与许可；随包附有 [Mindustry v160.7 的 GNU GPL 第 3 版许可证全文](records/reference-ui-sources/LICENSE-Mindustry-v160.7)。本说明不替换该许可证，也不将复制的上游源码宣称为本仓库作者的原创代码。各清单记录了对应文件、版本、源码位置或来源链接。

本次新增的道家 Q 版图片、控件、UI 布局预览及相关制作记录，和上述上游参考源码分别记录来源。图片使用 AI 生成，并按任务授权进行透明清理、裁切和部件组合；逐图记录位于图片旁的 `.generation.json`、`.derived.json` 或相应 worker 清单。`references/style/` 保存任务指定的既有风格参考及制作规则快照，这些文件不来自 Mindustry 官方素材库。

本次发布未另行指定新增美术与风格参考图的通用再许可条款。本说明不新增任何第三方材料的授权，也不将上游源码的 GPL 文件当作对全部新增图片统一授权的声明。复用具体材料时，应以其实际来源和适用许可为准。

本包包含从固定上游版本原样保留的 6 个运行时字体文件，并记录它们的路径与哈希；这些不是新增 AI 字体。离线 HTML 预览仍使用系统字体回退。静态美术验收不代表完整游戏客户端、服务端或运行时动画已完成接入。

字体内部的作者、版权及许可字符串，以及 Fontello 各来源字体的声明，保存在 [字体来源说明](full-game/runtime-visuals/font-notices/README.md)。Noto Sans JP 与 Fira Code 的 OFL、ProggyCleanTT 的 MIT 声明随包附带；Darktech LDR 保留 Michał “Neoqueto” Nowak 的署名及其内嵌 [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) 许可链接。六个字体文件均未修改。这些字体许可不由本说明替换。

新增品牌名为“天工仙阵”。`full-game/integration/upstream/ImageTileGenerator.java` 原样来自固定上游提交；它的自动拼接布局与算法用于构建运行时图块，版权和 GPL 来源按上述上游声明保留。美术模块的构建与接入源码随包提供，原游戏可执行 JAR 不随美术包重新分发。
