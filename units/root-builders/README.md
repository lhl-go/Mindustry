# Alpha / Beta / Gamma 核心建造单位

交付 3 张静态组合预览及 5 张原生独立层：Alpha、Beta、Gamma 各自的机体，Alpha 的 `small-basic-weapon`，Beta/Gamma 共用的 `small-mount-weapon`。官方武器定义来自固定 v160.7 `UnitTypes.java` 第 2494、2545、2596 行附近，镜像、偏移和 `top=false` 已记录。

机体与武器来自一张原生 1536×1024 RGBA 图板；请求目标 3072×2048 未达到。所有独立层只裁切、清理 alpha、加 32 px 留白；武器旋转 180° 使枪口朝上，没有放大或新造细节。机体大小与轮廓各有区别。

`assets/` 是静态组合参考；`layers/` 是接入用原生部件。组合参考中的武器按估算比例缩小，并遵从先武器、后机体的绘制顺序，因此部分枪身会被机体遮挡。实际像素到世界比例、挂点与可见枪口须在客户端校准。`estimated_art_alignment` 不是已验证的引擎参数。

独立层和组合图都通过 PNG、SHA、透明边界与深浅底检查。引擎喷流、采矿／建造光束、激光弹与后坐由官方逻辑实现，不烘焙进静态图。动画、队伍着色、世界尺寸与 atlas 装载尚未运行验收。

完整数据见 `../../records/workers/root-builders/manifest.json`、`verification.json` 及每张 PNG 同名 `.derived.json`。
