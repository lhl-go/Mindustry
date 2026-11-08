# Mindustry v160.7 单位图集导出

固定来源为 Anuken/Mindustry `17012d61d9e4c3cbd9820d87e81c24495486ac53`。`manifest.json` 覆盖全部 290 条原始单位 PNG 路径，逐项包含引擎文件与 SHA、原生美术文件与 SHA、原始画布尺寸、锚点、来源记录和消费者映射。

本批复用已完成的道家 Q 版独立身体、腿、武器与活动部件；补绘 6 个完整底座和关节组件。87 张生命色、发热和发光遮罩从新造型像素导出为白色 Alpha 遮罩，未使用旧造型轮廓。`conquer-glow` 对应新身体，`conquer-weapon-glow` 对应新炮塔，`conquer-weapon-sinks-heat` 对应新散热片；原源码的红色、加法混合与 warmup 运动仍保留。

`engine/core/assets-raw/sprites/units/` 按 290 条原始路径和原始像素尺寸输出。原生高清美术仍通过 `nativeFile` 指向正式素材，导出缩小不会被标称为新的原生高清。原始 `merui-weapon.png` 仅为 2×3 的占位区域，本包保留该画布兼容性，其完整高清武器仍在 `nativeFile`。

额外 `corvus-weapon`、`vela-weapon` 是身体分层后需要的独立炮塔基础图；`additionalAtlasRegions` 已给出准确 `sourceTreePath`，应复制到源码 `core/assets-raw/sprites/units/weapons/`，再参与正式图集构建。

五种坦克的源 `-treads` 已按官方 `treadRects` 排成左右完整布局。`generatedAtlasRegions` 的 144 张 1 像素宽纹理是官方生成器对新履带像素的移位结果：8 组矩形，每组 18 帧。正式接入应运行官方 `Generators.java` 构建路径，使用 `int(unit.treadTime()) % 18` 取帧并由运行时镜像与拉伸；这些帧是构建结果，不复制进源码 weapons 目录，也不覆盖源履带整板。

三个共用 atlas 名称 `large-bullet-mount`、`missiles-mount`、`large-artillery` 已各选定唯一图像，所有使用者与候选来源写入 `mappingConflictsResolved`。原冻结设计预览不被修改。

`qa/report.json` 保存 290 项尺寸、哈希、非空校验及 87 项遮罩边界校验；`qa/` 的 21 张验收联系表覆盖深浅底、遮罩、补绘组件和 144 帧。联系表中的青色与橙色是验收标色；原始遮罩为中性白色。小尺寸贴图在联系表中采用最近邻放大，便于检查像素。

本批完成美术与源码几何导出验收，尚未在 Mindustry 实机运行，因此所有资源保留 `engineNotVerified: true`。实际旋转、后坐、腿部运动及构建 atlas 的运行验证不作已完成声明。

逐图记录区分配置目标和实际工具证据：本次补绘使用宿主内置 image_gen，实际型号与质量未返回，记录为 null。所有本地切片、旋转、缩放、装配、遮罩和生成帧均保留完整派生链。

单位制作完成后，协调者核对正式文件、路径边界与 SHA256，已成功删除本批 292 张消费完的参考图、源板和临时图，全部成品与逐图来源文字仍保留。见 `retention-cleanup.json` 和 `../root-unit-source-cleanup.json`。此前其它明确文件的删除曾被自动审批拒绝，那些被拒文件没有重试删除，不属于本次 292 张。


坦克运动层修订：五种坦克身体已从当前正式原生图中分离对应运动带，保留静态轮架、端部装甲和全部其他绘画像素；新增 5 张 `revised-bodies/` 原生分层派生图，原始画布锚点不变。同步更新 5 张 cell 与 conquer-glow 遮罩。按官方 treads 先画、body 后画的顺序离线合成后，运动矩形可见面积为 68.67%—93.39%，第 0/9 帧可见变化为 1221—9365 像素。Conquer 前履带与身体在 alpha 16/128/245 阈值下均为一个主体连通域。报告见 `qa/tank-motion.json` 与 `qa/conquer-alpha-connectivity.json`。此验证是源码绘制顺序的离线像素模拟，游戏实机验证仍未执行。
