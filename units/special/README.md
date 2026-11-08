# 特殊单位与法器弹体

本目录交付固定 Mindustry v160.7 的 12 项独立静态美术、10 张附加分层，以及 4 张生成源板的来源文字记录（源图已在成品核验后清理）。全部为玉绿、象牙白、暖金的道家 Q 版手绘设计，朝向画布上方。每张图片旁的 `.generation.json` 记录原生尺寸、哈希与完整来源链；本地导出没有放大、重绘主体或生成新细节。

| 内容 | 独立图 | 分层 |
|---|---|---|
| 自动货运、装配、沙盒标靶 | `assets/manifold.png`、`assembly-drone.png`、`dummy.png` | 单体；货物、工具随主体绘制 |
| Renale | `assets/renale.png` | `layers/renale-segment0..2.png`，尾、躯干、头 |
| Latum | `assets/latum.png` | `layers/latum-segment0..3.png`，尾、后躯、前躯、头 |
| Anthicus、Quell、Scathe 及三种变体 | 对应 `assets/{id}.png` | 单体 |
| Disrupt 弹体 | `assets/disrupt-missile.png` | `layers/disrupt-missile-body.png`、`left-fin.png`、`right-fin.png` |

Renale 与 Latum 的各段使用相同尺寸的透明画布、共享中心；原生部件沿纵向平移，接点静态重叠 32 像素。分段顺序对应 `UnitType.drawCrawl`：segment0 先画尾部，最终段画头部。完整 PNG 是已有分段的合成预览。当前分段数量和静态接缝已检查；旋转、蠕动、世界尺寸和动态接缝尚未运行验收。

Disrupt 的独立左右尾翼保留于相同画布，静态合成顺序为左翼、右翼、主体。枢轴在 worker manifest 中标为 `estimated_art_alignment`；不是已经验证的客户端 RegionPart 参数。客户端需要按正式缩放和原版旋转参数重新检查铰点。

普通导弹、飞行单位的引擎光、尾迹、爆炸，Phase 护盾与 Surge 分裂计划复用官方程序效果，不烘焙在主体图片中。Surge 子弹体仅有一张，多个子弹体由运行时生成。`block` 是官方内部方块映射代理，没有独立图片。

透明处理只保留源板 alpha≥16 的对应连通部，清除外围低 alpha 隐藏 RGB，每个主体四周增加至少 32 像素透明安全边。已经在真实 alpha 合成的浅米底与深灰底逐项查看；原始 RGBA 查看器可能夸大低 alpha 隐藏颜色，正式验收以合成结果为依据。

当前 12 项状态是“静态美术已导出，客户端未验收”。尚未确认 atlas region 命名、像素到世界尺寸、队伍着色、阴影、动画、效果与游戏加载。详细清单、尺寸、来源坐标、层位移及检查记录见 `../../records/workers/special/manifest.json`。
