# 物品、液体、状态、弹丸与特效交付

固定源版本 Anuken/Mindustry v160.7，commit `17012d61d9e4c3cbd9820d87e81c24495486ac53`。

`manifest.json` 覆盖官方源树全部 164 条分配路径：33 物品/液体、20 状态、4 阵营、10 废墟、5 基础形状、52 effects、40 火焰。`file` 是高清原生切片或精确技术纹理，`engineFile` 保持官方 PNG 的真实画布尺寸，供原名 atlas 接入。它们的 SHA、尺寸和逐图生成记录均可查询。

其中 122 张由 14 次内置生图原生切片，8 张弹丸背层由对应新绘前层 Alpha 扩展派生，34 张为必须保持 UV/混合语义的官方技术纹理。美术主体保持道家 Q 版玉绿、米白、暖金风格，并保留各资源识别色。技术纹理明确标注为复用，未冒称重新绘制。

`fire.animation.json` 指定 40 帧、90 tick（1.5 秒）循环、2.25 tick/帧、中心锚点与 384×384 原生注册画布。`fire-loop.apng` 为透明预览；最终引擎帧仍为官方 100×100 画布。图片经过透明彩边清理、保留主体与原生细节，没有放大冒充高清。

`runtime-fx.json` 逐项保留 267 个 Fx 回调的精确源码、生命周期、静态 atlas 和动态输入依赖。Fill/Lines/Drawf 参数化绘制不应由单张静态图替代。`runtime-content.json` 明确映射 22 物品、11 流体和 23 状态；none、invincible、dynamic 没有独立原始图标。

`runtime-atlas.json` 闭合额外 128 个构建生成区域：16 bubble 与12 splash 技术圆环已按固定源码公式导出 PNG；100 个 fluid 区域保留官方 `Generators.java` 的精确算法及必要 `runtime-inputs/fluid.png` 原始遮罩。Mindustry 的原有 sprite packer 在构建时生成这 100 个区域，它们不是缺失的手绘图。液体与气体各 50 帧，运行时相位遵循 `Liquid.getAnimationFrame()`；Arc 依赖固定为 `gradle.properties` 中的 `7445105cd2`。

每张图旁 `.generation.json` 追溯实际母图、提示词、参考图和工具回执。配置目标与实际证据分开：本批使用内置 image_gen，宿主没有披露实际模型快照/质量，也没有提供选择器，故实际及提交型号/质量为 null。全部原生尺寸如实保存。

`qa/report.json` 和深浅底联系表记录像素、边界、哈希、原始尺寸与目视检查；没有运行 Mindustry 引擎，`engineNotVerified` 始终为 true。
