# Mindustry v160.7 地形与环境美术

固定来源为 Anuken/Mindustry `17012d61d9e4c3cbd9820d87e81c24495486ac53`。733 个官方图像路径均已映射，兼容 PNG 尺寸与官方源图一致。完成范围是静态美术与可追溯资源导出；未启动或验收实际客户端。

| 分类 | 路径数 | 实际处理 |
| --- | ---: | --- |
| 新绘地表、液体、矿石、墙、自然物、星球图标 | 349 | 23 批内置 image_gen 母图中的独立区域，清理、裁切并下采样 |
| 金属连接图及基础图 | 45 | 39 个独立新绘材质区域，保留官方连接几何、alpha 与结构明暗；6 个基础图共享对应材质 |
| 自然物阴影 | 17 | 从新绘主体实际 alpha 派生，不另称 AI 新画 |
| 星空 cube faces | 6 | 一张 1774×887 原生全景投影为 256×256 面图，另有 1024×1024 兼容重采样 |
| space shader 纹理 | 1 | 1254×1254 原生新绘纹理，另有 2048×2048 兼容重采样 |
| 官方技术资源 | 315 | 字形、符文、混合边缘、cliff masks、染色载体、shader 噪声及工具标记逐项说明并保留原字节 |

总计 25 次内置生成。提示词要求的尺寸不是实际返回尺寸；实际型号和质量未被宿主披露，均记录为 `null`。配置目标不作为实际锁定型号的证据。两张指定邮件/组队主参考均实际查看，并在每次调用的 `referenced_image_paths` 中附加；功能参考与风格参考角色分别记录。

主要入口：

- `manifest.json`：733 条官方路径 → `file` / `engineFile`、SHA-256、`nativeFile`、原生尺寸与来源记录；六个基础金属图共享材质，故 733 条 native 映射对应 727 个不同文件。
- `assets/`：按官方源路径排列的兼容输出，全部原版画布尺寸。
- `native/`：真实原生裁片、材质、原生比例阴影、256 面图与最终全景；没有把放大称为原生细节。金属的 nativeFile 是新绘材质，连接几何单独保存。
- `native/stars-equirectangular.png`：六面共同的最终全景设计输入；已列在 `nativeMasters`，不会漏包。
- `reference/` 中 45 个 `integrationGeometryInputs`：金属连接图重建所需原版几何输入。其他已消费参考不属于正式交付。
- `prompts/`、`source/*.generation.json`、`records/*.receipt.json`：精确提示词、完整工具参数、时刻、配置快照、返回路径、参考哈希与原图哈希。
- `qa/`、`records/final-visual-review.json`、`records/delivery-validation.json`：逐批目视与最终文件检查。原生样张见 `qa/28-native-detail-samples.png`。

运行约定：地表逻辑画布 32×32、每格 8 world units；矿石/道具采用透明 alpha。Floor 的 96×96 edge stencil、Cliff 的数据索引 mask 和金属连接几何保留原约定；本范围固定树没有独立 wall-normal PNG。单块地表重复接缝检查已通过，未改输入的旧结果复用。六面天空盒原生及兼容版本的 12 对相邻边逐像素一致，极点与经度边已检查；真实引擎过滤与朝向仍须接入测试。

`Planets.java` 的球体网格、云层与太阳，以及水面、粒子、雾、程序阴影等运行效果继续使用官方程序。新的两张星球 PNG 是静态图标，不能称作重绘了程序行星或全部动画。地形混合、随机变体、物体阴影注册、地图碰撞/寻路及移动端性能均未做客户端验收，本交付不是新关卡或可玩的地图。

官方保留与混合资源的许可、来源和理由在各自 `.source.json` / `.derived.json`；上游 LICENSE 保存在 `licenses/Mindustry-LICENSE.txt`。不把官方字形或技术贴图宣称为 AI 新绘。

素材保留：713 张已消费源板/参考副本的安全删除请求被自动审批以 `blocked by policy` 拒绝；没有重试或绕过，文件仍在本地。`retention-cleanup.json` 明确列出并从正式包排除；成品、必要45几何输入和来源文字全部保留。

制作工具 doctor 的 4 个 WARN 原文如下（该报告未定义数值阈值；并非美术失败）：

- `python.path`: `other python.exe on PATH: ~/AppData/Local/Programs/Python/Python313/python.exe; ~/AppData/Local/Microsoft/WindowsApps/python.exe`。实际使用记录中的 bundled Python 绝对路径。
- `deps.scipy`: `not installed; needed for faster labelling and keying (forge_core falls back to numpy)`。本批使用 NumPy 与扫描线连通域。
- `encoding.stdout`: `stdout=gbk: non-ASCII text can be garbled in pipes`。执行使用 `-X utf8`。
- `encoding.files`: `open() and read_text() without encoding= use cp936`。读写显式指定 UTF-8。

完整可选工具 MISSING 信息保留在 `doctor.json`；未安装这些可选 CLI/视频工具，不影响本次内置静态生图路线。没有宣称所有工具或运行验收通过。
