# D/C 状态与移动布局审查

交付 `ui/preview/dialog-component-variants.js` 和同名 CSS。脚本定义全局 `enhanceDialogComponent()`，仅在 dialog/component 页面替换 DOM；页面切回 screen 时移除本模块样式标记。协调者已将脚本放在 `preview.js` 前加载，并在 render 内调用该 hook，样式放在现有样式之后。本 worker 没有编辑 index、preview.js、preview.css、inventory 或屏幕变体文件。

16 组对话框按 stateIndex 补齐了确认禁用、输入错误、长文、四种暂停上下文、结算、创建房间等待/失败、配装容量/库存、战役难度、过滤、颜色、文件表单、追踪/全局变量、元信息、尺寸校验、黑白名单及效果播放反馈。20 组组件板各格与 requiredDesignStates 一一对应，组内全状态同时展示。

重点修复：C-06 的焦点框、选中文本和插入光标分别可见；C-12 为三格，格内分别包含满/部分/空、增/减、警告；C-15 用自身定位的小地图，移动端嵌入与展开尺寸不同；C-09 的纵/横/细轨道随真实滚动位置更新；C-20 标题缩短以免压住装饰。移动视口为现有合同的 844×390，正文独立滚动，footer 固定留在窗内。

按 v160.7 源文件额外纠正了三处语义：HostDialog 的名称是玩家名称并带玩家颜色，仅好友是 Steam 条件项；CampaignRulesDialog 使用五档难度及战争迷雾等真实开关；MapResizeDialog 宽高范围为 50–800，SectorGenerateDialog 的区块编号从 0 开始。

`browser-audit.json` 记录了 140 状态 × 2 视口的 280 次实际 Chrome 渲染，检查增强 hook、正文横向溢出、footer 边界、缺图、组件格数及对话框正文差异，均通过。9 项交互/滚动检查通过。控制台无脚本或资源错误，忽略项仅 favicon 404。每组首页及风险状态已截图，21 张代表图通过 `view_image` 单独查看；没有把全 280 项都声称为人工目视通过。

复验命令：使用 bundled Node 执行 `records/workers/ui-audit/audit.cjs`，预览服务应位于 `http://127.0.0.1:8765/ui/preview/`。该脚本不启动真实游戏、不创建房间、不写入示例文件。效果播放为本地 CSS 反馈，客户端粒子效果仍未验收。
