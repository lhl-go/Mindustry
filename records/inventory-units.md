# Mindustry v160.7 单位美术映射

核查：2026-10-26T04:00:39-04:00。固定 [v160.7](https://github.com/Anuken/Mindustry/releases/tag/v160.7) / [17012d6](https://github.com/Anuken/Mindustry/commit/17012d61d9e4c3cbd9820d87e81c24495486ac53)；机器清单见 [inventory-units.json](inventory-units.json)。本次未生成图片。

**56 个常规单位＋2 个建筑自动无人机＝58 个正常玩法视觉单位**。另有 2 个隐藏生物、1 个沙盒标靶、1 个内部建筑代理、7 个导弹实体，共 69 个实例化内容 ID；69 不是可玩角色数或最终 PNG 数。依据：[UnitTypes](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java)、[Blocks](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/Blocks.java)。

## 分组及全量 ID

中文名来自固定版本 [中文包](https://github.com/Anuken/Mindustry/blob/v160.7/core/assets/bundles/bundle_zh_CN.properties#L1839)；未提供表示缺少 unit.name 键。分类是排产口径，交叉移动/辅助属性在 JSON。

### 地面（21）

| ID | 官方中文名 | 范围 |
| --- | --- | --- |
| [dagger](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L100) | 尖刀 | 常规生产/升级 |
| [mace](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L121) | 战锤 | 常规生产/升级 |
| [fortress](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L153) | 堡垒 | 常规生产/升级 |
| [scepter](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L190) | 权杖 | 常规生产/升级 |
| [reign](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L291) | 王座 | 常规生产/升级 |
| [crawler](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L661) | 爬虫 | 常规生产/升级 |
| [atrax](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L701) | 毒蛛 | 常规生产/升级 |
| [spiroct](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L744) | 血蛭 | 常规生产/升级 |
| [arkyid](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L810) | 毒蛊 | 常规生产/升级 |
| [toxopid](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L914) | 天蝎 | 常规生产/升级 |
| [stell](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L2654) | 围护 | 常规生产/升级 |
| [locus](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L2700) | 循迹 | 常规生产/升级 |
| [precept](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L2783) | 准绳 | 常规生产/升级 |
| [vanquish](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L2857) | 征服 | 常规生产/升级 |
| [conquer](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L2969) | 领主 | 常规生产/升级 |
| [merui](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L3153) | 天守 | 常规生产/升级 |
| [cleroi](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L3239) | 天赐 | 常规生产/升级 |
| [anthicus](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L3349) | 天灾 | 常规生产/升级 |
| [tecta](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L3507) | 天理 | 常规生产/升级 |
| [collaris](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L3615) | 天帝 | 常规生产/升级 |
| [elude](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L3789) | 挣脱 | 常规生产/升级 |

### 空中（9）

| ID | 官方中文名 | 范围 |
| --- | --- | --- |
| [flare](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L1047) | 星辉 | 常规生产/升级 |
| [horizon](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L1091) | 天垠 | 常规生产/升级 |
| [zenith](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L1140) | 苍穹 | 常规生产/升级 |
| [antumbra](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L1187) | 月影 | 常规生产/升级 |
| [eclipse](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L1263) | 日蚀 | 常规生产/升级 |
| [avert](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L3858) | 遮蔽 | 常规生产/升级 |
| [obviate](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L3923) | 消散 | 常规生产/升级 |
| [quell](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L4044) | 遏止 | 常规生产/升级 |
| [disrupt](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L4149) | 悲怆 | 常规生产/升级 |

### 海军（10）

| ID | 官方中文名 | 范围 |
| --- | --- | --- |
| [risso](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L1577) | 梭鱼 | 常规生产/升级 |
| [minke](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L1638) | 飞鲨 | 常规生产/升级 |
| [bryde](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L1700) | 戟鲸 | 常规生产/升级 |
| [sei](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L1798) | 蛟龙 | 常规生产/升级 |
| [omura](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L1892) | 海神 | 常规生产/升级 |
| [retusa](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L1943) | 潜螺 | 常规生产/升级 |
| [oxynoe](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L2051) | 电鳗 | 常规生产/升级 |
| [cyerce](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L2132) | 江豚 | 常规生产/升级 |
| [aegires](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L2273) | 玄武 | 常规生产/升级 |
| [navanax](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L2325) | 龙王 | 常规生产/升级 |

### 建造（6）

| ID | 官方中文名 | 范围 |
| --- | --- | --- |
| [alpha](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L2494) | 阿尔法 | 核心建造 |
| [beta](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L2545) | 贝塔 | 核心建造 |
| [gamma](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L2596) | 伽马 | 核心建造 |
| [evoke](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L4354) | 苏醒 | 核心建造 |
| [incite](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L4420) | 策动 | 核心建造 |
| [emanate](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L4499) | 发散 | 核心建造 |

### 辅助（12）

| ID | 官方中文名 | 范围 |
| --- | --- | --- |
| [nova](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L357) | 新星 | 常规生产/升级 |
| [pulsar](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L397) | 恒星 | 常规生产/升级 |
| [quasar](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L452) | 耀星 | 常规生产/升级 |
| [vela](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L498) | 灾星 | 常规生产/升级 |
| [corvus](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L585) | 死星 | 常规生产/升级 |
| [mono](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L1345) | 独影 | 常规生产/升级 |
| [poly](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L1364) | 幻型 | 常规生产/升级 |
| [mega](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L1422) | 巨像 | 常规生产/升级 |
| [quad](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L1473) | 雷霆 | 常规生产/升级 |
| [oct](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L1547) | 要塞 | 常规生产/升级 |
| [manifold](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L4582) | 货运无人机 | 建筑自动调用 |
| [assembly-drone](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L4609) | 装配无人机 | 建筑自动调用 |

### 特殊（11）

| ID | 官方中文名 | 范围 |
| --- | --- | --- |
| [anthicus-missile](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L3465) | 未提供 | 武器衍生弹体 |
| [quell-missile](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L4115) | 未提供 | 武器衍生弹体 |
| [disrupt-missile](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L4236) | 未提供 | 武器衍生弹体 |
| [renale](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L4309) | Renale | 隐藏/无常规产线 |
| [latum](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L4329) | Latum | 隐藏/无常规产线 |
| [block](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L4572) | 未提供 | 内部建筑代理 |
| [dummy](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/UnitTypes.java#L4635) | 未提供 | 沙盒标靶 |
| [scathe-missile](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/Blocks.java#L5257) | 未提供 | 武器衍生弹体 |
| [scathe-missile-phase](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/Blocks.java#L5345) | 未提供 | 武器衍生弹体 |
| [scathe-missile-surge](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/Blocks.java#L5450) | 未提供 | 武器衍生弹体 |
| [scathe-missile-surge-split](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/Blocks.java#L5506) | 未提供 | 武器衍生弹体 |

## 可共享系列

前 12 条为常规生产/核心系列，后 2 条为建筑自动与隐藏内容。可以共用材质、纹样与设计语言，每个 ID 都需独立文件和来源记录。多足、助推、负载、盾向、武器层逐个核对，不能用一张图放大换色代替。生产关系见 [Blocks](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/Blocks.java#L6298)。

| 系列 | ID | 道家美术提案与共享边界 |
| --- | --- | --- |
| Serpulo 地面火力 | dagger, mace, fortress, scepter, reign | 符甲机关卫；独立双足与枪炮轮廓 |
| Serpulo 地面支援 | nova, pulsar, quasar, vela, corvus | 玉莲阵法机关；独立修复光束、护盾及腿部结构 |
| Serpulo 突击爬行 | crawler, atrax, spiroct, arkyid, toxopid | 机关虫兽；爆破、毒液、吸能与重装多足分别制作 |
| Serpulo 空中火力 | flare, horizon, zenith, antumbra, eclipse | 飞鸢／灵禽机关；翼型、投弹口、导弹及重激光独立 |
| Serpulo 空中辅助 | mono, poly, mega, quad, oct | 采矿葫芦、修造浮器及护阵运载机关；独立工具与负载挂点 |
| Serpulo 海军火力 | risso, minke, bryde, sei, omura | 龙舟机关舰；各级独立船体、炮塔及水迹层 |
| Serpulo 海军支援 | retusa, oxynoe, cyerce, aegires, navanax | 玉螺／玄甲水上机关；治疗、点防御与压制装置独立 |
| Serpulo 核心建造 | alpha, beta, gamma | 御器建造机关；各型独立体量、工具及推进结构 |
| Erekir 履带战车 | stell, locus, precept, vanquish, conquer | 玄甲履带机关；独立底盘与炮位，不以缩放代替升级 |
| Erekir 多足机甲 | merui, cleroi, anthicus, tecta, collaris | 阵甲多足灵械；独立足肢、反导、导弹、盾向与火炮 |
| Erekir 悬浮／空中线 | elude, avert, obviate, quell, disrupt | 悬浮符舟至压制飞舟；elude 悬浮底盘与其余飞行单位分开 |
| Erekir 核心建造 | evoke, incite, emanate | 维修御器与建造机关；载荷、光束和工程武器分别分层 |
| 建筑附属无人机 | manifold, assembly-drone | 货运葫芦与装配浮器；货舱和装配工具独立 |
| 隐藏 Neoplasm 生物 | renale, latum | 分节瘴灵异兽；3 节小体与 4 节大体独立 |

7 个导弹应独立对应母武器；Scathe 本版含普通、phase、surge、surge-split 四类。dummy 制作机关标靶，block 不设计独立人物。依据：[MissileUnitType](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/type/unit/MissileUnitType.java)、[Scathe](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/content/Blocks.java#L5257)、[TargetDummy](https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/world/blocks/defense/TargetDummy.java#L28)。

## 判定与未核实项

- ID 为构造器中的内容字符串，不是运行时数字 ID；assemblyDrone 的内容 ID 为 assembly-drone。
- 穷举 UnitTypes.load 的 65 个构造和 Blocks.load 的 4 个附加导弹构造；Bullets.java 未见 UnitType 构造。
- 分组为本项目排产口径：海军支援留在海军，地面／空中支援归辅助；建造核心单列。
- elude 位于官方 Erekir 飞行系列，但 flying=false、hovering=true，按地面悬浮计数。
- hidden 不代表没有画面：manifold、assembly-drone 有建筑宿主；dummy 用于沙盒标靶。
- UnitTypes.missile 仅有 EntityDef 代码生成声明，无同名构造实例，不计第70个 ID。
- legacy=true 属实体代码生成兼容，不表示已废弃兵种。
- isEnemy 表示计入波次敌人统计，不等同固定阵营；effectiveFlags 为静态初始化推导，不是运行时补丁后值。
- Latum/Renale 在中文包中仍为拉丁名；内部实体和导弹没有 name 键时保持 null，不自造官方译名。
- 58 个正常玩法视觉单位；dummy 沙盒目标、2 个隐藏生物、7 个弹体单列。69 不是可玩角色数或最终 PNG 数。
- 道家改编保留机关、灵兽、御器的功能与移动轮廓，不全部换成人像；每个 ID 独立文件，不能用简单放大换色替代。

- 未启动客户端或加载 Mod／数据补丁，未确认运行时数字 ID。
- 未逐个核对 atlas region、像素尺寸、旋转锚点、武器/腿/负载层与动画帧；本清单不能代表美术交付完成。
- Neoplasm 两单位在核查的工厂、核心、科技树没有常规获取入口；是否启用隐藏内容与沙盒标靶需按项目功能范围决定。
- 原创设计方向未批准为正式角色文案；已有道童概念稿不可抵扣原单位完成数量。
- REST tag 元数据请求连接中断，tag→commit 改由官方发布页的提交链接确认。

本地官方源缓存位于 `reference-unit-sources/`，原 URL 和 SHA256 在 JSON；没有克隆仓库或改动 Git。
