# Mindustry 功能与接入核对

2026-10-26，只读核实官方源；以下概念改编建议不是原版已有美术。

- [官方仓库](https://github.com/Anuken/Mindustry)：Java；工厂自动化、塔防与 RTS，包含客户端及独立服务端构建。
- [服务端说明](https://mindustrygame.github.io/wiki/servers/)：独立服务端以终端操作、无图形界面。本任务绘制客户端和联机入口，不凭空制作所谓原版服务端 GUI。
- HUD 与建造功能入口：[HudFragment.java](https://raw.githubusercontent.com/Anuken/Mindustry/master/core/src/mindustry/ui/fragments/HudFragment.java)、[PlacementFragment.java](https://raw.githubusercontent.com/Anuken/Mindustry/master/core/src/mindustry/ui/fragments/PlacementFragment.java)。
- 联机与研究入口：[JoinDialog.java](https://raw.githubusercontent.com/Anuken/Mindustry/master/core/src/mindustry/ui/dialogs/JoinDialog.java)、[ResearchDialog.java](https://raw.githubusercontent.com/Anuken/Mindustry/master/core/src/mindustry/ui/dialogs/ResearchDialog.java)，样式入口 [Styles.java](https://raw.githubusercontent.com/Anuken/Mindustry/master/core/src/mindustry/ui/Styles.java)。
- [单位定义](https://github.com/Anuken/Mindustry/blob/master/core/src/mindustry/content/UnitTypes.java) 与官方单位页：[Alpha](https://mindustrygame.github.io/wiki/content/units/35-alpha/)、[Dagger](https://mindustrygame.github.io/wiki/content/units/0-dagger/)、[Flare](https://mindustrygame.github.io/wiki/content/units/15-flare/)。后续可分别探索建造御器单位、符甲机关卫、灵鹤飞械；不是官方角色名称。
- [Mod 图片接入说明](https://mindustrygame.github.io/wiki/modding/4-spriting/)：`sprites/units`、`sprites/blocks`、`sprites/items`，覆盖既有图片为 `sprites-override/`。高清 UI 概念和人物立绘不可直接冒充可加载贴图；需另行验证俯视形态、层级、旋转、尺寸及命名。

不依据旧文案中的 GitHub 星数判断当前热度，不将源码或服务端开发并入本轮美术启动批次。
