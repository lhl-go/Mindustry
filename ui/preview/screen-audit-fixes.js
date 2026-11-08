/* Focused screen-state corrections from the final independent audit. */
const SA_AFFECTED_IDS=['UI-004','UI-009','UI-011','UI-012','UI-014','UI-018','UI-019','UI-021','UI-022','UI-023','UI-025','UI-026','UI-027','UI-028'];
function saButton(text,kind='',action='ack'){return `<button type="button" class="btn ${kind}" data-sa-action="${action}">${esc(text)}</button>`;}
function saStack(...items){return `<div class="sa-stack">${items.join('')}</div>`;}
function saTwo(left,right){return `<div class="sa-two">${left}${right}</div>`;}
function saFrame(title,body,actions){return windowFrame(title,body,actions||btn('返回','','nav:UI-001')+saButton('完成','primary'));}
function saMapLegend(){return '<div class="sa-marker-key"><span>● 己方玩家</span><span class="error">● 敌方单位</span><span>◆ 己方核心</span><span>▱ 当前视域</span></div>';}
function saMap(){return '<div class="sa-map">'+map()+'<span class="sa-core">◆ 核心</span><span class="sa-player">青云</span></div>';}
function saWaveRows(){return rows([['尖刀 · 组 1','第 1–10 波 · 每波 4 个','drone',badge('红队')],['战锤 · 组 2','第 5–20 波 · 每波 2 个','turret',badge('红队')],['星辉 · 组 3','第 10–30 波 · 每波 3 个','drone',badge('空中')]]);}
function saWaveFields(){return control('开始波次',field('1','','number'))+control('结束波次',field('10','','number'))+control('间隔波次',field('1','','number'))+control('单位数量',field('4','','number'))+control('数量增长',field('1','','number'))+control('护盾',field('120','','number'))+control('护盾增长',field('15','','number'))+control('首领',toggle(true));}

function enhanceScreenAudit(){
 const view=document.querySelector('#gameViewport'),id=currentId,i=stateIndex;
 const active=group.kind==='screen'&&SA_AFFECTED_IDS.includes(id);view.classList.toggle('sa-preview',active);if(!active)return;
 let html=null;
 if(id==='UI-004'){
  if(i===1)html=saFrame('战术地图',saStack('<div class="sa-map sa-map-plain">'+map()+'</div>',hint('地图已展开，可拖动查看地形。')),saButton('缩小')+saButton('放大')+btn('返回','','nav:UI-002'));
  if(i===2)html=saFrame('战术地图 · 标记',saTwo(saStack(saMap(),saMapLegend()),pane('地图标记',control('显示玩家',toggle())+control('显示敌方',toggle())+control('显示核心',toggle())+control('显示视域',toggle())+stat('青云','核心西侧')+stat('敌方单位','东北方向 · 2 个'))),btn('返回','','nav:UI-002'));
 }
 if(id==='UI-009'&&i===2)html=saFrame('地图详情与模式',saTwo(pane('双河防线',saMap()+stat('作者','内置地图')+stat('尺寸','320 × 320')),pane('模式选择',control('游戏模式',options(['生存','沙盒','PvP','攻击']))+stat('建议玩家','1–4')+hint('生存：持续建设防线，抵御来袭波次。')+btn('自定义规则','','nav:UI-020'))),saButton('返回地图列表','','state:0')+saButton('开始游戏','primary'));
 if(id==='UI-011'&&i===1)html=saFrame('内容详情 · 属性分类',saStack(tabs(['基础','攻击','弹药','建造']),saTwo(pane('基础属性',stat('名称','双管炮')+stat('生命','250')+stat('尺寸','1 × 1')),pane('攻击与弹药',stat('射程','13.75 格')+stat('射速','2 × 3 发 / 秒')+stat('弹药类型','铜 / 石墨 / 硅'))),pane('建造需求',stat('铜','35')+stat('前置科技','机械钻头'))));
 if(id==='UI-011'&&i===2)html=saFrame('内容详情 · 战役解锁',saTwo(pane('双管炮',icon('turret','big')+badge('当前战役未解锁','muted')+stat('所属研究树','赛普罗')),pane('解锁条件',stat('前置研究','尚未完成')+hint('请先在对应星球的研究树中满足前置条件。')+btn('查看研究树','primary','nav:UI-006'))),saButton('返回内容详情','','state:0'));
 if(id==='UI-012'&&i===2)html=saFrame('蓝图详情',saTwo(pane('基础铜矿生产线',`<div class="sa-blueprint">${icon('blueprint','big')}<span>3 × 8</span></div>`+stat('标签','生产 / 基础')+hint('选中蓝图的整体范围与物资需求。')),pane('建造需求',stat('铜','120')+stat('铅','45')+stat('建筑数量','12')+btn('编辑标签','','modal:D-13')+saButton('复制到剪贴板','','copy'))),saButton('返回蓝图库','','state:0')+saButton('放置蓝图','primary'));
 if(id==='UI-014'){
  const search=`<div class="toolbar">${field('','搜索模组','search','data-search')}${options(['最近更新','星数','发布日期'],i===0?1:0)}${saButton('刷新','small')}</div>`;
  const list=rows([['青云外观包','美术 · v1.0','mods',badge('已安装')],['工坊地图集','地图 · v2.3','planet',badge('可下载')],['机械挑战','内容 · v1.2','mods',badge('可下载')]]);
  const detail=icon('mods','big')+stat('版本','1.0.0')+stat('适用版本','v160.7');
  if(i===0)html=saFrame('模组浏览 · 搜索排序',saStack(search,saTwo(pane('浏览结果',list),pane('排序条件',stat('排序','星数')+stat('筛选结果','3 个')+hint('输入名称可以过滤列表。')))),saButton('关闭'));
  if(i===1)html=saFrame('模组浏览 · 加载中',`<div class="sa-loading"><div class="loading" aria-label="加载中"></div><h2>正在加载模组目录…</h2><p>等待目录响应，尚无可选择的结果。</p></div>`,saButton('取消'));
  if(i===2)html=saFrame('模组详情 · 已安装',saTwo(pane('青云外观包',detail+badge('已安装')),pane('说明与依赖','<p>提供界面与单位的美术外观。</p>'+stat('作者','示例作者')+stat('依赖','无')+hint('本机已安装此版本。')+btn('管理已安装模组','','nav:UI-013'))),saButton('返回列表','','state:0')+'<button class="btn primary" disabled>已安装</button>');
  if(i===3)html=saFrame('选择发行版本',saTwo(pane('青云外观包',detail),pane('可用发行版',rows([['v1.1.0','最新 · 适用 v160.7','mods',badge('已选')],['v1.0.0','当前安装','mods',badge('已安装')],['v0.9.0','历史版本','mods',badge('旧版','muted')]])+control('发行版本',options(['v1.1.0','v1.0.0','v0.9.0'])))),saButton('取消')+saButton('下载所选版本','primary'));
  if(i===4)html=saFrame('下载与依赖状态',saTwo(pane('下载任务',stat('模组','机械挑战')+stat('进度','4.5 / 10 MB')+bar(45)+hint('连接中断，下载未完成。',true)),pane('依赖处理',stat('需要依赖','机关基础包')+badge('尚未安装','danger')+hint('重试后将一并检查依赖。'))),saButton('取消')+saButton('重试','primary'));
 }
 if(id==='UI-018'){
  const properties=view.querySelector('.editorProperties');
  if(i===2){properties.innerHTML='<h4>网格显示</h4>'+control('显示网格',toggle(true))+stat('网格状态','已显示')+hint('格线已显示，用于对齐建筑与地形。');view.querySelector('.mapSurface')?.classList.add('gridlines');}
  if(i===3){properties.innerHTML='<h4>撤销与重做</h4>'+saStack(saButton('撤销上一步','','undo'),saButton('重做下一步','','redo'),stat('已撤销','放置双管炮'),stat('下一步重做','放置双管炮'),hint('当前预览保留一项可重做操作。'));view.querySelector('.mapSurface')?.insertAdjacentHTML('beforeend','<div class="sa-history-marker">已撤销的建筑位置</div>');}
 }
 if(id==='UI-019'){
  if(i===0)html=saFrame('地图生成 · 滤镜列表',saTwo(pane('滤镜顺序',rows([['噪声','基础地形','settings'],['扭曲','调整边缘','refresh'],['河流','生成水系','conveyor']])+saButton('查看空列表','small','empty-filters')),pane('生成预览',saMap()+hint('滤镜按列表顺序应用。'))),saButton('取消')+saButton('添加滤镜','primary','',''));
  if(i===2)html=saFrame('地图生成 · 参数编辑',saTwo(pane('噪声参数',control('强度',range(65))+control('缩放',range(40))+control('阈值',range(35))+control('地表',options(['石头','沙地','浅水']))),pane('当前预览',saMap()+stat('选中滤镜','噪声'))),saButton('取消')+saButton('更新预览','primary'));
  if(i===3)html=saFrame('地图生成 · 随机与应用',saTwo(pane('随机参数',control('随机种子',field('56412','','number','data-sa-seed'))+saButton('重新随机','small','random-seed')+stat('滤镜数量','4')+hint('生成参数已更新，应用前可查看右侧预览。')),pane('待应用预览',saMap()+badge('预览已更新'))),saButton('取消')+saButton('应用生成结果','primary'));
  if(i===4)html=saFrame('地图生成 · 参数管理',saTwo(pane('滤镜参数文本','<textarea class="field sa-code-input" aria-label="滤镜参数">[{"type":"noise","scale":40},{"type":"river","width":3}]</textarea>'),pane('参数操作',saStack(saButton('复制参数','','copy'),saButton('粘贴参数','','paste'),saButton('重置所有滤镜','danger','reset-preview'),hint('这些操作仅展示参数管理状态。')))),saButton('返回生成器','','state:0'));
 }
 if(id==='UI-021'){
  if(i===1)html=saFrame('波次 · 添加单位组',saTwo(pane('选择单位',cards([['尖刀','drone','地面'],['战锤','turret','地面'],['星辉','drone','空中']],'three')),pane('新单位组',control('起始波次',field('11','','number'))+control('结束波次',field('20','','number'))+control('初始数量',field('6','','number'))+badge('尚未添加'))),saButton('取消')+saButton('添加单位组','primary'));
  if(i===2)html=saFrame('波次 · 搜索与排序',saStack(`<div class="toolbar">${field('尖刀','搜索单位组','search','data-search')}${options(['起始波次','单位名称','数量'])}${options(['全部单位','地面单位','空中单位'],1)}</div>`,pane('筛选结果 · 1 个单位组',rows([['尖刀 · 组 1','第 1–10 波 · 每波 4 个','drone',badge('匹配')]])),hint('当前筛选：地面单位，名称包含“尖刀”。')),saButton('清除筛选','','state:0'));
  if(i===3)html=saFrame('波次 · 单位组参数',saTwo(pane('数量与波次',saWaveFields()),pane('第 10 波预览',icon('turret','big')+stat('单位','战锤')+stat('首领状态','已启用')+stat('护盾','120')+hint('区间、增长与护盾参数分别编辑。'))));
  if(i===4)html=saFrame('波次 · 队伍与出生点',saTwo(pane('部署规则',control('队伍',options(['红队','蓝队','绿队']))+control('出生点',options(['全部','出生点 1 · 北侧','出生点 2 · 东侧'],1))+stat('当前单位组','尖刀 · 组 1')+hint('该单位组仅从北侧出生点出现。')),pane('出生点示意',saMap()+saMapLegend())));
 }
 if(id==='UI-022'){
  if(i===2)html=saFrame('目标 · 节点与连线',saTwo(pane('已选节点',control('目标名称',field('建立防线'))+control('建筑',options(['双管炮','机械钻头']))+control('数量',field('3','','number'))+badge('当前选中')),pane('前置与后续','<div class="sa-flow"><span>采集 100 铜</span><b>→</b><strong>建造 3 座炮塔</strong><b>→</b><span>抵御第 10 波</span></div>'+hint('选中节点在前置目标完成后开始检查。'))));
  if(i===3)html=saFrame('目标 · 世界标记',saTwo(pane('标记属性',control('形状',options(['圆形','文本','箭头','区域'],3))+control('X / Y',field('128, 64'))+control('标签',field('防御区域'))+control('颜色','<input type="color" value="#d4ac55">')+control('显示标记',toggle())),pane('标记示意',saMap()+badge('防御区域','gold'))));
  if(i===4)html=saFrame('目标 · 剪贴板与清空',saTwo(pane('目标数据',stat('目标节点','4')+stat('世界标记','1')+'<pre class="code">采集 100 铜 → 建造防线\n→ 抵御第 10 波 → 区域完成</pre>'),pane('管理操作',saStack(saButton('复制目标','','copy'),saButton('粘贴目标','','paste'),saButton('清空所有目标','danger','clear-objectives'),hint('清空操作将在预览中显示确认状态。')))),saButton('返回目标图','','state:0'));
 }
 if(id==='UI-023'&&i===3)html=saFrame('世界处理器 · 管理',saTwo(pane('选中处理器',icon('database','big')+stat('当前位置','128, 128')+stat('指令数量','5')),pane('重命名与删除',control('名称',field('核心控制'))+saButton('应用名称','primary')+hint('删除只影响所选处理器。',true)+saButton('删除处理器','danger','confirm-delete'))),saButton('返回列表','','state:0'));
 if(id==='UI-025'){
  if(i===1)html=saFrame('地图文本 · 属性搜索',saStack(`<div class="toolbar">${options(['简体中文','English','日本語'])}${field('description','搜索属性名或值','search','data-search')}</div>`,pane('搜索结果 · 1 个属性',rows([['map.description','一座机关与河流交织的工坊','blueprint',badge('匹配')]])),hint('按属性名或文本值搜索；当前仅显示 description。')),saButton('清除搜索','','state:0'));
  if(i===3)html=saFrame('地图文本 · 多语言编辑',saTwo(pane('属性内容',control('属性名',field('map.description'))+'<textarea class="field sa-code-input" aria-label="属性值">一座机关与河流交织的工坊</textarea>'),pane('应用范围',control('当前语言',options(['简体中文','English','日本語']))+control('应用到所有语言',toggle(false))+hint('当前只修改所选语言；勾选后应用到所有语言。'))),saButton('取消')+saButton('应用文本','primary'));
  if(i===4)html=saFrame('地图文本 · 编辑工具',saTwo(pane('待编辑文本','<textarea class="field sa-code-input" aria-label="待编辑文本">守护核心</textarea>'),pane('工具',saStack(btn('插入图标','','modal:D-09'),saButton('恢复原文','','restore-original'),saButton('导入文本','','import-preview'),saButton('复制属性','','copy')))),saButton('返回文本列表','','state:0'));
 }
 if(id==='UI-026'&&i===1)html=saFrame('地图资源 · 图片导入',saTwo(pane('待导入图片',`<div class="sa-blueprint">${icon('blueprint','big')}<span>banner.png</span></div>`+stat('文件类型','PNG')+stat('尺寸','256 × 128')),pane('图片属性',control('资源名称',field('banner'))+stat('目标','当前地图资源包')+hint('资源名称必须在当前地图内唯一。')+saButton('选择图片文件','','import-preview'))),saButton('取消')+saButton('导入图片','primary','import-preview'));
 if(id==='UI-027'&&i===1)html=saFrame('画布 · 颜色与调色板',saTwo(pane('当前颜色',`<div class="sa-color-preview"></div>`+control('颜色值',field('#4B8E65'))+control('颜色','<input type="color" value="#4b8e65">')+btn('详细颜色选择','','modal:D-10')),pane('调色板',`<div class="palette sa-palette">${['#173d35','#397565','#76a67b','#c0d1a1','#fff4d9','#d7bb76','#a67c42','#9c4836','#4b8e65','#e8d9b3','#96b5bf','#6e627c','#e5ad84','#d0a07a','#685c46','#292d29'].map((c,n)=>`<button style="background:${c}" aria-label="${c}" data-color="${c}" class="${n===8?'sa-color-selected':''}"></button>`).join('')}</div>`+stat('当前选择','第 9 色 · #4B8E65')+hint('颜色与画布操作分开选择。'))),saButton('返回画布','','state:0')+saButton('应用颜色','primary'));
 if(id==='UI-027'&&i===2)html=saFrame('画布 · 图像导入导出',saTwo(pane('当前画布',`<div class="sa-blueprint">${icon('research','big')}<span>32 × 32 · 16 色</span></div>`),pane('PNG 文件',saStack(saButton('选择 PNG 导入','','import-preview'),saButton('导出当前画布','','export-preview'),hint('导入图片需满足当前画布的尺寸和颜色数量限制。'),stat('当前状态','尚未选择外部文件')))),saButton('返回画布','','state:0'));
 if(id==='UI-028'&&i===1)html=saFrame('聊天 · 历史与输入',saTwo(pane('频道',tabs(['全部','队伍'],1)+stat('当前频道','队伍')+stat('在线玩家','3')+hint('当前消息仅向队伍频道发送。')),pane('聊天记录','<div class="chatLog sa-chat"><div class="chatMessage"><b>青云</b>核心西侧需要更多铜矿供给。</div><div class="chatMessage"><b>玄工</b>运输线已接通，正在补充炮塔。</div><div class="chatMessage"><b>山海</b>下一波还有 38 秒。</div></div><form class="toolbar" data-chat>'+field('已收到，正在修复西侧防线。','输入消息','text','name="message" required maxlength="160"')+btn('发送','primary','send')+'</form>')),btn('玩家列表','','nav:UI-028')+saButton('关闭'));
 if(html!==null)view.innerHTML=html;
 view.dataset.auditState=`${id}:${i}`;
}

document.addEventListener('click',event=>{
 const target=event.target.closest('[data-sa-action]');if(!target)return;event.preventDefault();event.stopPropagation();
 const action=target.dataset.saAction;
 if(action.startsWith('state:')){stateIndex=+action.slice(6);render();return;}
 if(action==='random-seed'){const input=document.querySelector('[data-sa-seed]');input.value=String((+input.value+7919)%100000);toast('随机参数已更新（预览）');}
 else if(action==='empty-filters'){const panel=target.closest('.subpane');panel.innerHTML='<h3>滤镜列表</h3>'+empty('尚未添加滤镜');}
 else if(action==='clear-objectives'||action==='confirm-delete'){toast('已显示危险操作预览，未删除游戏数据');target.textContent='确认操作（预览）';target.classList.add('primary');}
 else if(action==='undo'||action==='redo'){toast(action==='undo'?'已撤销：放置双管炮（预览）':'已重做：放置双管炮（预览）');}
 else toast('本地交互预览，未执行游戏、文件或剪贴板操作');
},true);
