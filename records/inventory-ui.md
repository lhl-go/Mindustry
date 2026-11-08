# Mindustry v160.7 · UI 生产清单

固定官方版本：[`v160.7`](https://github.com/Anuken/Mindustry/releases/tag/v160.7)，完整提交 `17012d61d9e4c3cbd9820d87e81c24495486ac53`。2026-10-26 核对。机器清单：[inventory-ui.json](inventory-ui.json)。

已读取并映射 67 个官方界面类：`ui/dialogs`、`ui/fragments`、编辑器 `*Dialog`、`LogicDialog` 与 `GlobalVarsDialog`，映射遗漏 0。逐类来源、缓存 SHA256、生产组映射保存于 JSON 的 `sourceClassCoverage`。官方树未截断，缓存为 [official-tree-v160.7.json](reference-ui-sources/official-tree-v160.7.json)。

**28 个独立设计面＋16 个复用弹窗族＋20 个共用组件族，共 64 个生产组；所有美术状态均为 pending。** 分组数量不是要求生成 64 张整屏，也不代表任一素材已完成。每个设计面需要各自状态图；通用模板仍须映射全部实际字段与来源类。状态、优先级、批次和复用关系属于本次美术计划，从源码功能归纳；官方类事实以链接为准。

## 独立设计面

| ID | 设计面 | 优先级 | 固定版本官方来源 |
| --- | --- | --- | --- |
| UI-001 | 主菜单与入口 | P0 | [MenuFragment.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/fragments/MenuFragment.java) |
| UI-002 | 实战 HUD／建造与建筑配置 | P0 | [HudFragment.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/fragments/HudFragment.java)、[PlacementFragment.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/fragments/PlacementFragment.java)、[BlockConfigFragment.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/fragments/BlockConfigFragment.java)、[BlockInventoryFragment.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/fragments/BlockInventoryFragment.java)、[PlanConfigFragment.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/fragments/PlanConfigFragment.java)、[MobileInput.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/input/MobileInput.java) |
| UI-003 | 单位指挥与姿态 HUD | P0 | [PlacementFragment.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/fragments/PlacementFragment.java) |
| UI-004 | 展开战术小地图 | P1 | [MinimapFragment.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/fragments/MinimapFragment.java)、[Minimap.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/Minimap.java) |
| UI-005 | 战役星球、区块与区域详情 | P0 | [PlanetDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/PlanetDialog.java) |
| UI-006 | 科技研究树 | P0 | [ResearchDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/ResearchDialog.java) |
| UI-007 | 联机服务器浏览与加入 | P0 | [JoinDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/JoinDialog.java) |
| UI-008 | 存档读取与保存槽管理 | P1 | [LoadDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/LoadDialog.java)、[SaveDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/SaveDialog.java) |
| UI-009 | 自定义对局地图与模式选择 | P1 | [CustomGameDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/CustomGameDialog.java)、[MapListDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/MapListDialog.java)、[MapPlayDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/MapPlayDialog.java) |
| UI-010 | 内容数据库目录 | P1 | [DatabaseDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/DatabaseDialog.java) |
| UI-011 | 内容详情与属性统计 | P1 | [ContentInfoDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/ContentInfoDialog.java) |
| UI-012 | 蓝图库、详情与标签编辑 | P1 | [SchematicsDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/SchematicsDialog.java) |
| UI-013 | 已安装模组管理 | P1 | [ModsDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/ModsDialog.java) |
| UI-014 | 模组浏览与下载详情 | P1 | [ModBrowserDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/ModBrowserDialog.java)、[ModsDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/ModsDialog.java) |
| UI-015 | 设置中心与数据管理 | P0 | [SettingsMenuDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/SettingsMenuDialog.java)、[LanguageDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/LanguageDialog.java) |
| UI-016 | 按键绑定 | P1 | [KeybindDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/KeybindDialog.java) |
| UI-017 | 编辑器地图库 | P1 | [EditorMapsDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/EditorMapsDialog.java)、[MapListDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/MapListDialog.java) |
| UI-018 | 地图编辑工作台 | P1 | [MapEditorDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/editor/MapEditorDialog.java) |
| UI-019 | 地图生成滤镜编辑器 | P2 | [MapGenerateDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/editor/MapGenerateDialog.java) |
| UI-020 | 自定义规则编辑器 | P1 | [CustomRulesDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/CustomRulesDialog.java) |
| UI-021 | 波次编排编辑器 | P2 | [WaveInfoDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/editor/WaveInfoDialog.java) |
| UI-022 | 地图目标与标记编辑器 | P2 | [MapObjectivesDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/editor/MapObjectivesDialog.java)、[MapObjectivesCanvas.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/editor/MapObjectivesCanvas.java) |
| UI-023 | 世界处理器管理 | P2 | [MapProcessorsDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/editor/MapProcessorsDialog.java) |
| UI-024 | 逻辑处理器编程工作台 | P1 | [LogicDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/logic/LogicDialog.java)、[LCanvas.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/logic/LCanvas.java)、[LStatements.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/logic/LStatements.java)、[GlobalVarsDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/logic/GlobalVarsDialog.java) |
| UI-025 | 地图本地化文本编辑器 | P2 | [MapLocalesDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/editor/MapLocalesDialog.java) |
| UI-026 | 地图自定义资源管理 | P2 | [MapAssetsDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/editor/data/MapAssetsDialog.java) |
| UI-027 | 像素画布与调色板编辑 | P2 | [CanvasEditDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/CanvasEditDialog.java)、[PaletteDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/PaletteDialog.java) |
| UI-028 | 联机玩家列表与聊天覆盖层 | P1 | [PlayerListFragment.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/fragments/PlayerListFragment.java)、[ChatFragment.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/fragments/ChatFragment.java) |

每个设计面的 `requiredDesignStates`、`sharedComponents` 和功能范围在 JSON 中逐项列明；桌面与移动端、建造与指挥、普通与空态等不得用一张示例图全部标通过。

## 复用弹窗

| ID | 模板族 | 覆盖的官方类 |
| --- | --- | --- |
| D-01 | 确认与危险操作确认 | [UI.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/core/UI.java)、[BaseDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/BaseDialog.java) |
| D-02 | 文字／数字输入与重命名 | [UI.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/core/UI.java) |
| D-03 | 信息、错误、长文、链接与关于 | [UI.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/core/UI.java)、[FullTextDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/FullTextDialog.java)、[AboutDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/AboutDialog.java)、[DiscordDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/DiscordDialog.java) |
| D-04 | 暂停菜单 | [PausedDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/PausedDialog.java) |
| D-05 | 战斗结算与战役完成 | [GameOverDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/GameOverDialog.java)、[CampaignCompleteDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/CampaignCompleteDialog.java) |
| D-06 | 创建联机房间 | [HostDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/HostDialog.java) |
| D-07 | 发射与资源配装 | [LaunchLoadoutDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/LaunchLoadoutDialog.java)、[LoadoutDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/LoadoutDialog.java) |
| D-08 | 战役难度与选项 | [CampaignRulesDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/CampaignRulesDialog.java) |
| D-09 | 搜索列表／图标／区域／语言选择 | [IconSelectDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/IconSelectDialog.java)、[SectorSelectDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/SectorSelectDialog.java)、[MapLoadDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/editor/MapLoadDialog.java)、[LanguageDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/LanguageDialog.java) |
| D-10 | 颜色选择 | [ColorPicker.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/ColorPicker.java) |
| D-11 | 文件选择／保存 | [FileChooserDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/FileChooserDialog.java)、[FileChooser.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/FileChooser.java) |
| D-12 | 管理记录列表与详情 | [AdminsDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/AdminsDialog.java)、[BansDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/BansDialog.java)、[TraceDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/TraceDialog.java)、[GlobalVarsDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/logic/GlobalVarsDialog.java) |
| D-13 | 元信息表单 | [MapInfoDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/editor/MapInfoDialog.java)、[SchematicsDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/SchematicsDialog.java) |
| D-14 | 尺寸／偏移／区域生成参数 | [MapResizeDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/editor/MapResizeDialog.java)、[SectorGenerateDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/editor/SectorGenerateDialog.java) |
| D-15 | 禁用内容选择 | [BannedContentDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/editor/BannedContentDialog.java)、[CustomRulesDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/CustomRulesDialog.java) |
| D-16 | 开发效果预览 | [EffectsDialog.java](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/EffectsDialog.java) |

复用是框板、标题、排版与控件复用，不删除原功能字段。例：创建房间仍需要名称／端口／创建中与失败状态，发射配装仍需要资源和容量。独立服务端没有在此增加虚构图形管理页。

## 共用组件

- **C-01 框板／标题／关闭／全屏与小窗**：普通窗／全屏窗／标题／分隔线／关闭。主参考的玉绿标题与米白正文，边框九宫格需单独合同。 [源码](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/Styles.java)
- **C-02 文字按钮**：up／over／down／disabled。主要／次要／危险按钮共享尺寸系列，文字使用原生字体。 [源码](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/Styles.java)
- **C-03 切换按钮、页签与菜单**：普通／悬停／按下／checked／disabled。选中与禁用必须可区分。 [源码](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/Styles.java)
- **C-04 图标按钮、工具栏与建筑选择框**：普通／悬停／按下／选中／禁用。图标不嵌按钮文字，保持小尺寸可读轮廓。 [源码](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/Styles.java)
- **C-05 中文文字、标题、数字与等宽代码**：正文／标题／说明／错误／mono。交付字体与排版规则，不把全部文字烘焙进控件。 [源码](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/Fonts.java)
- **C-06 单行、多行、数字输入框**：默认／焦点／选择／光标／禁用／无效。输入内容、选区和光标由引擎控制。 [源码](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/Styles.java)
- **C-07 复选框和规则开关**：未选／选中／禁用。沿用玉绿选中、米白普通层级。 [源码](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/Styles.java)
- **C-08 滑条与拖动柄**：轨道／普通柄／悬停柄／数值变化。参数数值为原生文字。 [源码](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/Styles.java)
- **C-09 滚动区和滚动条**：纵向／横向／细条／无条。圆角窗内不破坏独立滚动和底部固定操作。 [源码](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/Styles.java)
- **C-10 列表行、资源卡与选择网格**：普通／选中／禁用／空态／有错误。地图、存档、模组和单位卡共用皮肤变体，内容图独立映射。 [源码](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/dialogs/MapListDialog.java)
- **C-11 研究／目标节点和连线**：锁定／可用／选中／已完成／连线。科技图与目标图共用材质，不能共用功能图数据。 [源码](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/Styles.java)
- **C-12 状态条、资源栏与警告条**：满／部分／空／增加／减少／警告。血量、核心、构建、容量等有一致语义颜色。 [源码](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/Bar.java)
- **C-13 物品数量、成本与需求状态**：满足／不足／多选需求／数量。来源资源图标可复用；缺货不只靠颜色表达。 [源码](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/ItemsDisplay.java)
- **C-14 提示、通知、教程与告警**：tooltip／toast／淡出消息／教程提示／告警。不遮挡主操作，文字在客户端排版。 [源码](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/core/UI.java)
- **C-15 小地图框与标记**：嵌入／展开／敌我／核心／视域标记。地图数据与静态框分离。 [源码](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/Minimap.java)
- **C-16 加载／保存提示与过渡**：加载中／取消／完成淡出。动态进度组件不能以静态图宣称已实现动画。 [源码](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/fragments/LoadingFragment.java)
- **C-17 选中圈、世界提示与光标**：采矿／卸载／目标／修理／单位选中。保留实际操作含义；俯视世界标记与UI按钮分开。 [源码](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/core/UI.java)
- **C-18 移动端操作控件**：未按／按下／选中／可用／不可用。触控按钮和响应布局单独核验，桌面设计不能默认视为移动端完成。 [源码](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/MobileButton.java)
- **C-19 控制台与性能覆盖层**：输入／历史／错误输出／性能数据显示。以代码文字与轻量面板复用，不添加虚构管理功能。 [源码](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/fragments/ConsoleFragment.java)
- **C-20 编辑器画布、格线、选择与属性工具**：格线开关／画布缩放平移／选择／工具选中／参数编辑。逻辑和地图使用共用工具材质，功能画布分别保留。 [源码](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/editor/MapEditorDialog.java)

## 建议制作批次

1. **01-foundation 基础控件与主菜单／双模式HUD**：C-01、C-02、C-03、C-04、C-05、C-06、C-07、C-08、C-09、C-10、C-12、C-13、C-14、UI-001、UI-002、UI-003、D-01、D-02、D-03、D-04、D-05。
1. **02-campaign 战役、研究、区域与发射**：UI-004、UI-005、UI-006、D-07、D-08、C-11、C-15、C-17。
1. **03-multiplayer 联机列表、房主与玩家聊天**：UI-007、UI-028、D-06、D-12。
1. **04-libraries 地图、存档、内容与蓝图库**：UI-008、UI-009、UI-010、UI-011、UI-012、D-09、D-11。
1. **05-settings-mods 设置、键位、模组与平台状态**：UI-013、UI-014、UI-015、UI-016、C-16、C-18、C-19。
1. **06-editor 地图编辑基础与规则**：UI-017、UI-018、UI-020、D-13、D-14、D-15、C-20。
1. **07-advanced-editor 高级编辑器与专用工具**：UI-019、UI-021、UI-022、UI-023、UI-024、UI-025、UI-026、UI-027、D-10、D-16。

## 仍需补充或验证

- **GAP-01 具体建筑的动态配置内容 — pending_source_expansion**：BlockConfigFragment 由具体 Building.buildConfiguration 填充；world/blocks 下的全部覆盖尚未在本次 UI 类盘点中逐类穷举。需要对内置建筑配置覆写做后续专项扫描，并映射 UI-002 或新增专用控件变体，不能把此项当作完成。 [源码依据](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/ui/fragments/BlockConfigFragment.java)
- **GAP-02 地图资源类型专用编辑行 — pending_source_expansion**：地图资源管理调用各资源类型的编辑构建器；editor/data 中条目的专用内容需要追加资源类型清单，当前 UI-026 是管理框架。 [源码依据](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/editor/data/MapAssetsDialog.java)
- **GAP-03 平台条件与运行布局 — pending_runtime_validation**：本次是固定源码盘点，没有运行客户端。桌面/移动/Steam 条件、分辨率、滚动、字段长度及真实控件状态须在接入验收确认。

其中 GAP-01 与 GAP-02 是明确的未完成范围，不能以“67 类已映射”替代。该统计覆盖内置 UI 类注册面，尚非所有动态建筑配置／资源编辑变体的最终穷尽清单。第三方模组自定义页面、原生系统文件窗口、字体实现和布局算法不独立生图。

## 美术完成条件

每项存在真实本地资产或可验证复用映射；各必需状态已检查；图像来源、模型/质量证据、原生尺寸和 SHA256 完整；透明边缘与可读性问题已关闭；切片、锚点、图层和资源功能映射可追溯。概念设计、正式控件、客户端运行验收分别记录。当前所有生产组尚未因此清单获得完成状态。

