# Serpulo 地面与海军单位

本目录交付固定 Mindustry v160.7 的 25 个单位。Alpha、Beta、Gamma 由 `units/root-builders` 交付，不计入本目录。官方名称、源码行号和每个实例的资源映射见 [manifest.json](manifest.json)。协调者读取的同内容清单位于 `records/workers/serpulo-ground-naval/manifest.json`。

文件共包含 25 张完整单位静态预览、20 张独立机体和 30 张可复用部件；另直接引用 `units/serpulo-root-parts/layers` 的 5 张支援舰船体。部件包含 24 种武器以及轻型、重型、爬虫双足腿和多足单位的上腿、下腿、足部。所有完整单位都是独立透明 PNG，完整预览不替代分层机体。

| 文件 | 用途 |
|---|---|
| `sprites/{id}.png` | 25 个完整单位的静态装配预览，朝上；包含机体、实际武器数量及对应腿数。 |
| `bodies/{id}.png` | 20 个机体原生裁切，未放大，无独立武器及行走肢体。 |
| `parts/*.png` | 可独立使用的武器和腿部原生裁切，未放大。 |
| `manifest.json` | 身份、尺寸、SHA256、锚点、层文件、实例变换、官方 region 映射和来源记录。 |
| `qa-light.jpg`、`qa-dark.jpg` | 已检查的浅、深背景联系表；仅为设计与透明边缘验收证据。 |
| `*.generation.json` | 每个最终图的完整来源链和实际处理说明。 |

原始生成采用内置 `image_gen`，实际提交提示词位于 `prompts/serpulo-ground-naval`。当次配置目标是 GPT Image 2.5 / max；宿主工具没有型号和质量选择器，也没有返回这两项元数据，因此各图的实际型号和实际质量均明确记为未确认。裁切、透明清理、缩小、翻转和装配由用户明确授权的本地像素处理完成，不表示重新生图。静态装配的画布尺寸不等同于原生生成尺寸。

美术验收已完成：25 张单位的真实 Alpha 范围均为 0–255，完整留白，主体连通，未检测到孤立微小杂点；浅、深、灰三底目视检查通过。根协调者另外查看了浅、深联系表。完整报告在 `records/workers/serpulo-ground-naval/final-validation.json`。

引擎接入尚未验证。`layerMapping` 记录官方原始 region，`layers` 给出每个实例在预览中的锚点、位置、缩小比例与旋转；这些是新机体的美术坐标，不是已经校准的世界坐标。上腿和下腿原图长轴沿 Y，接入 Mindustry `Lines.line` 时需要在图集适配中转到 X 轴；内嵌关节纹样可代替可选的独立关节覆盖层。队色遮罩、动画、炮口反冲、弹道、能量场和水迹由客户端运行时处理。本包没有声称已在游戏中运行。

最终导出及来源核验后，按用户素材保留规则删除了拒稿、只用于切分的源板和临时检查图；不保留图片备份。原生源图的尺寸、SHA256、时间、工具回执、输入图哈希、配置快照与提示词保留在 `records/workers/serpulo-ground-naval`，并标记 `sourceImageRetained:false`。删除记录见 `retention-cleanup.json`。源板删除后不要直接重跑 `build_assets.py`；已有机体、部件和 manifest 是当前维护对象。
