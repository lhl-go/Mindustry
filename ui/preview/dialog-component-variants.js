/* D/C visual state variants. Preview-only: no game, filesystem or network actions. */
function dcButton(text, kind='', action='ack', disabled=false) {
  return `<button type="button" class="btn ${kind}" data-dc-action="${action}" ${disabled?'disabled':''}>${esc(text)}</button>`;
}
function dcField(value='',extra='') { return field(value,'请输入内容','text',extra); }
function dcNumber(value,min=0,max=9999,extra='') { return field(value,'','number',`min="${min}" max="${max}" ${extra}`); }
function dcStack(...items) { return `<div class="dc-stack">${items.join('')}</div>`; }
function dcChoices(labels,selected=0) { return `<div class="dc-choices" role="group">${labels.map((x,i)=>`<button type="button" class="tab ${i===selected?'selected':''}" data-dc-choice aria-pressed="${i===selected}">${esc(x)}</button>`).join('')}</div>`; }
function dcNotice(text,error=false) { return `<div class="hint ${error?'error':''}" role="status">${esc(text)}</div>`; }
function dcEmpty(message='没有匹配内容') { return `<div class="dc-empty">${icon('search')}<strong>${esc(message)}</strong><small>调整搜索条件后重试</small></div>`; }
function dcList(items) { return `<div class="list searchable dc-list">${items.map((r,i)=>row(r[0],r[1]||'',r[2]||'folder',r[3]||'',r[4]===true)).join('')}</div>`; }
function dcChecks(labels,checked=[]) { return `<div class="dc-checks">${labels.map((x,i)=>control(x,toggle(checked.includes(i)))).join('')}</div>`; }
function dcMap(kind='embedded') { return `<div class="dc-map dc-map-${kind}"><div class="mapSelection"></div><i class="mapMarker" style="left:24%;top:58%" title="己方单位"></i><i class="mapMarker enemy" style="left:74%;top:25%" title="敌方单位"></i><span class="dc-core" style="left:43%;top:48%" title="己方核心">◆</span>${kind==='markers'?'<div class="dc-map-key">● 己方　<span class="error">● 敌方</span>　◆ 核心　▱ 视域</div>':''}</div>`; }

function dcDialogVariant() {
  let title=group.name,body='',actions=dcButton('取消')+dcButton('确认','primary'),size='compact';
  const i=stateIndex;
  switch(currentId) {
    case 'D-01':
      title=['确认操作','确认删除','暂时无法继续'][i];
      body=dcStack(`<div class="dc-message">${icon(i===1?'close':'settings','big')}<h2>${['应用当前更改？','删除“云海工坊”？','当前存档仍在写入'][i]}</h2><p>${['确认后将使用新的规则设置。','此操作会移除所选存档，无法撤销。','请等待保存结束，再执行删除操作。'][i]}</p></div>`,i===2?dcNotice('保存进行中 · 删除已禁用',true):i===1?dcNotice('建议先导出需要保留的数据。',true):'');
      actions=dcButton(i===2?'关闭':'取消')+dcButton(i===1?'删除':'确认',i===1?'danger':'primary','ack',i===2);break;
    case 'D-02':
      title=i===2?'输入数量':'重命名';
      body=dcStack(control(i===2?'数量（1–100）':'新名称',i===2?dcNumber(24,1,100,'aria-label="数量"'):dcField(i===1?'':'云海工坊',`aria-label="新名称" ${i===1?'aria-invalid="true"':'data-dc-focused'}`)),i===1?dcNotice('名称不能为空。请输入 1–32 个字符。',true):dcNotice(i===2?'仅接受整数，范围 1–100。':'最多 32 个字符，名称可继续编辑。'));
      actions=dcButton('取消')+dcButton('确认','primary','ack',i===1);break;
    case 'D-03':
      size=i===1?'medium':'compact';title=['提示','操作说明','错误详情','关于 天工仙阵'][i];
      if(i===0) body=dcStack(icon('save','big'),'<h2>保存完成</h2>','<p>“云海工坊”已保存，可继续游戏。</p>');
      if(i===1) body=`<article class="dc-longtext" tabindex="0" aria-label="可滚动操作说明">${['建立第一条生产线','保持资源运输畅通','守住核心','建造与修复','指挥单位','战役研究','保存与联机','检查供电'].map((s,n)=>`<h3>${n+1}. ${s}</h3><p>从铜矿附近开始铺设生产线。检查设施的输入与输出，保持传送带方向一致，并为核心和防御建筑持续供应资源。选中建筑查看状态，按需补充弹药和电力。</p>`).join('')}</article>`;
      if(i===2) body=dcStack(dcNotice('地图读取失败：文件格式不兼容。',true),'<pre class="code"><span class="err">MapException: unsupported map data</span>\nFile: workshop.msav\nExpected version: v160.7\nAction: select a compatible file</pre>',dcButton('复制错误详情','small','copy-preview'));
      if(i===3) body=dcStack('<h2>天工仙阵</h2>','<p>工厂自动化 · 塔防 · RTS</p>',stat('功能基线','v160.7'),stat('原项目作者','Anuken'),'<h3>贡献者</h3><p>代码、翻译、地图和社区贡献者</p>','<div class="dc-linkrow"><a href="https://mindustrygame.github.io/" target="_blank" rel="noreferrer">官方网站 ↗</a><a href="https://github.com/Anuken/Mindustry" target="_blank" rel="noreferrer">项目与贡献者 ↗</a></div>');
      actions=dcButton('关闭','primary');break;
    case 'D-04':
      title=['游戏已暂停','战役已暂停','联机房主菜单','编辑器测试暂停'][i];
      body=dcStack(badge(['单机 · 云海工坊','战役 · 冰冻森林','房主 · 3 名玩家','编辑器 · 地图测试'][i]),`<div class="dc-pause-menu">${btn('继续游戏','primary','nav:UI-002','play')}${btn('设置','','nav:UI-015','settings')}${i===2?btn('玩家列表','','nav:UI-028','network')+dcButton('管理房间','','room-preview'):i===3?btn('返回编辑器','','nav:UI-018','settings'):btn('保存游戏','','nav:UI-008','save')}${i===1?btn('战役地图','','nav:UI-005','planet'):i===0?btn('读取存档','','nav:UI-008','folder'):''}${btn('返回主菜单','danger','nav:UI-001')}</div>`);
      actions=dcButton('关闭');break;
    case 'D-05':
      title=['战斗结束','区域丢失','连接中断','战役完成'][i];
      body=dcStack(`<h2 class="${i<2?'error':''}">${['核心已被摧毁','冰冻森林已丢失','等待其他玩家重新连接','所有目标已完成'][i]}</h2>`,i===0?dcNotice('PvP 结果示例：蓝队获胜，绿队失败。'):i===1?dcNotice('本区建筑与物资已丢失，可从邻接区域重新发射。',true):i===2?'<div class="loading" aria-label="等待中"></div>'+dcNotice('与房主失去连接，当前结算尚未完成。',true):dcNotice('恭喜完成战役。可以返回星球继续建设。'),i!==2?stat('到达波次','25')+stat('游戏时间','42 分钟')+stat('摧毁敌人','328'):stat('连接状态','已断开 · 等待重连'));
      actions=i===2?dcButton('返回菜单')+dcButton('重新连接','primary','reconnect-preview'):btn('返回战役','','nav:UI-005')+dcButton(i===3?'继续建设':'重新开始','primary');break;
    case 'D-06':
      title=i===2?'正在创建房间':'创建联机房间';
      body=dcStack(control('玩家名称',dcField('青云',i===2?'disabled maxlength="40"':'maxlength="40"')),control('玩家颜色','<input type="color" value="#4b8e65" aria-label="玩家颜色" '+(i===2?'disabled':'')+'>'),control('端口',dcNumber(6567,1,65535,i===2?'disabled':i===3?'aria-invalid="true"':'')),i===1?control('仅好友可见',toggle(true)):'',i===1?dcNotice('Steam 平台选项：仅好友能够发现并加入此房间。'):i===2?'<div class="dc-inline"><div class="loading"></div><span>正在准备房间…</span></div>':i===3?dcNotice('地址已被占用（端口 6567）。更换端口后重试。',true):dcNotice('其他玩家可通过主机地址加入。'));
      actions=dcButton('取消')+dcButton(i===2?'创建中…':i===3?'重试':'创建房间','primary','host-preview',i===2);break;
    case 'D-07':
      title='发射配装';size='medium';
      body=`<div class="dc-two">${pane('核心蓝图',cards([['初代核心','planet','容量 4,000'],['基础工坊','blueprint','生产布局']],'three')+dcNotice(i===0?'已选择：初代核心。选择另一张卡可切换蓝图。':'当前蓝图：初代核心'))}${pane('携带物资',control('铜',dcNumber(i===2?2800:i===3?1800:1200))+control('铅',dcNumber(i===2?1000:600))+control('硅',dcNumber(i===2?200:180))+stat('容量',i===2?'4,000 / 4,000':i===3?'2,580 / 4,000':'1,980 / 4,000')+bar(i===2?100:i===3?65:49,i===2)+(i===2?dcNotice('容量已满，无法继续增加物资。',true):i===3?dcNotice('铜库存仅 640，尚缺 1,160；当前配置不能发射。',true):i===1?dcNotice('数量可编辑，携带物资受容量与库存限制。'):''))}</div>`;
      actions=dcButton('取消')+dcButton('发射','primary','launch-preview',i===3);break;
    case 'D-08':
      title=['选择战役难度','战役规则选项','区域失败后处理'][i];
      body=i===0?dcStack(dcChoices(['休闲','简单','正常','困难','毁灭'],2),stat('当前难度','正常'),dcNotice('难度影响敌军血量、敌军数量与波次间隔。')):i===1?dcStack(dcChecks(['敌方入侵区块','战争迷雾','隐藏敌人出生点','不可预测的 AI 波次','禁用暂停'],[0,1]),dcNotice('入侵选项仅在允许区块入侵的星球显示。')):dcStack(control('重置丢失区块',toggle(true)),dcNotice('区块失守后，不保留上次尝试中建造的建筑。'),dcNotice('仅在星球未强制重置丢失区块时提供此开关。'));
      break;
    case 'D-09':
      title=['选择语言','当前语言','搜索语言'][i];
      body=dcStack(`<div class="toolbar">${icon('search')}${field(i===2?'English':'','搜索语言','search','data-search aria-label="搜索语言"')}</div>`,i===0?dcList([['简体中文','中文界面','database'],['English','English interface','database']])+dcNotice('无结果示例：搜索不存在的语言时显示空态。')+dcEmpty('没有匹配的语言'):i===1?dcList([['简体中文','当前使用','database',badge('当前'),true],['English','English interface','database'],['日本語','日本語表示','database']]):dcList([['English','1 个筛选结果','database',badge('匹配')]])+dcNotice('过滤条件：English · 1 / 3'));
      break;
    case 'D-10':
      title='选择颜色';size='medium';
      body=`<div class="dc-two"><div class="dc-stack"><div class="dc-color-plane" aria-label="饱和度与亮度选择区域"><i></i></div><div class="dc-inline">${'<div class="dc-checker"><div class="colorSwatch" style="background:#4b8e65'+(i===2?'80':'')+'"></div></div>'}<span>${i===2?'透明度 50%':'当前色 #4B8E65'}</span></div></div><div class="dc-stack">${i===0?stat('原颜色','#397565')+stat('当前颜色','#4B8E65'):i===1?control('色相',range(42))+control('饱和度',range(65))+control('亮度',range(70)):control('透明度',range(50))+control('颜色值',dcField('#4B8E6580','aria-label="RGBA颜色值"'))}${dcNotice(['当前颜色与原颜色可对照。','拖动滑条调整颜色。','颜色值包含透明度通道。'][i])}</div></div>`;break;
    case 'D-11':
      title=i===3?'保存文件':'选择文件';size='medium';
      body=dcStack(`<div class="toolbar">${field('maps/','目录','text','aria-label="目录"')}${dcButton('上级','small')}</div>`,i===1?control('文件筛选',options(['地图与存档 (*.msav)','蓝图 (*.msch)','所有文件'])):'',dcList(i===1?[['workshop.msav','地图文件 · 256 KB','planet']]:[['campaign','文件夹','folder'],['workshop.msav','地图文件 · 256 KB','planet'],['defense.msch','蓝图文件 · 8 KB','blueprint']]),i>=2?control('文件名',dcField(i===3?'new-map.msav':'workshop.msav','aria-label="文件名"')):'',i===1?dcNotice('仅显示 *.msav，蓝图文件已过滤。'):i===3?dcNotice('目标：maps/new-map.msav。按钮仅演示，不写入文件。'):i===2?dcNotice('名称可编辑，扩展名需与文件类型一致。'):'');
      actions=dcButton('取消')+(i===3?dcButton('打开现有','', 'file-preview'):'')+dcButton(i===3?'保存':'打开','primary','file-preview');break;
    case 'D-12':
      title=['管理员与封禁','管理记录','玩家追踪详情','全局变量'][i];size='medium';
      body=i===0?`<div class="dc-two">${pane('管理员',dcList([['青云','当前房间 · 房主','network',badge('管理员')]]))}${pane('封禁列表',dcList([['玩家 02','违反房间规则','network',dcButton('解除封禁','small')]]))}</div>`:i===1?dcStack(dcChoices(['管理员','封禁','追踪']),dcEmpty('暂无管理记录')):i===2?dcStack(stat('玩家','玄工'),stat('玩家 ID','demo-player-02'),stat('地址','192.0.2.24（示例）'),stat('最后连接','2026-10-26 09:30'),stat('加入次数','3'),stat('修改方块','42'),dcNotice('示例追踪数据，仅当前面板展示。')):`<div class="dc-two">${pane('系统',dcList([['@wave','12','database'],['@time','1480.5','database']]))}${pane('世界',dcList([['objectiveComplete','false','database'],['coreResources','1240','database']]))}</div>`;
      actions=dcButton('关闭','primary');break;
    case 'D-13':
      title=['地图信息','蓝图信息','关联编辑'][i];
      body=i===2?dcStack(stat('地图','云海工坊'),'<div class="dc-link-menu">'+btn('编辑规则','','nav:UI-020')+btn('编辑波次','','nav:UI-021')+btn('编辑目标','','nav:UI-022')+btn('本地化文本','','nav:UI-025')+'</div>'):dcStack(control(i===1?'蓝图名称':'地图名称',dcField(i===1?'基础铜矿生产线':'云海工坊')),i===0?control('作者',dcField('青云')):'','<label class="label">说明<textarea class="field" aria-label="说明">'+(i===1?'紧凑的铜矿运输线，连接核心后即可供货。':'为运输与防线预留空间的工坊地图。')+'</textarea></label>',i===1?control('标签',dcField('生产, 基础')):'');break;
    case 'D-14':
      title=['调整地图尺寸','区域生成参数','参数校验'][i];
      body=i===1?dcStack(control('星球',options(['赛普罗','埃里克尔'])),control('区块',field('24','','number','min="0" aria-label="区块"')),control('种子',dcNumber(10248,-2147483648,2147483647)),dcNotice('区块编号从 0 开始，必须小于所选星球的区块总数。')):i===2?dcStack(control('宽度（有效）',dcNumber(256,50,800)),control('高度（无效）',dcNumber(0,50,800,'aria-invalid="true"')),dcNotice('宽高必须在 50–800 之间。修正后才能应用。',true)):dcStack(control('宽度',dcNumber(256,50,800)),control('高度',dcNumber(256,50,800)),control('偏移 X',field('0','','text','maxlength="4" inputmode="numeric"')),control('偏移 Y',field('0','','text','maxlength="4" inputmode="numeric"')),dcNotice('宽高范围 50–800；偏移为整数，将改变现有地形的放置范围。'));
      actions=dcButton('取消')+dcButton('应用','primary','ack',i===2);break;
    case 'D-15':
      title='禁用内容';size='medium';
      body=dcStack(dcChoices(['建筑','单位'],i===3?1:0),`<div class="toolbar">${icon('search')}${field(i===1?'不存在的内容':'','搜索内容','search','data-search')}</div>`,i===1?dcEmpty():`<div class="dc-ban-grid">${['双管炮','机械钻头','电力节点','建造单位'].map((x,n)=>`<label class="dc-ban-item">${icon(['turret','drill','power','drone'][n])}${toggle(i===2||n===0)}<span>${x}</span></label>`).join('')}</div>`,i===2?`<div class="toolbar">${dcButton('全选','small','check-all')}${dcButton('清空','small','check-none')}<span>当前选中 4 项</span></div>`:i===3?dcStack(control('白名单模式',toggle(true)),dcNotice('白名单：仅勾选的内容允许使用；取消此开关后，勾选项将被禁用。')):dcNotice(i===1?'没有内容匹配当前搜索。':'黑名单：勾选项在当前规则中被禁用。'));
      break;
    case 'D-16':
      title='效果预览';size='medium';
      body=`<div class="dc-two"><div class="dc-stack"><div class="toolbar">${field('','搜索效果','search','data-search')}</div>${dcList([['建造完成','完成提示','drill',dcButton('播放','small','effect')],['修复粒子','修复脉冲','settings',dcButton('播放','small','effect')],['核心受击','告警闪光','turret',dcButton('播放','small','effect')]])}</div><div class="dc-effect-stage ${i===1?'dc-effect-playing':''}">${icon('drill','big')}<div class="dc-effect-ring"></div><span class="dc-effect-caption">${i===1?'正在预览：建造完成':'点击左侧播放按钮'}</span></div></div>`;
      actions=dcButton('关闭');break;
  }
  return windowFrame(title,body,actions,size);
}

function dcComponentExamples() {
  const states=group.requiredDesignStates;
  switch(currentId) {
    case 'C-01':return [pane('普通窗口','正文与底部操作分区'),'<div class="dc-mini-window"><b>全屏窗口</b><div>内容滚动区域</div><footer>返回　确认</footer></div>',`<div class="dc-title-sample">标题牌</div><hr class="dc-divider">`,'<button class="close dc-close-example" type="button" aria-label="关闭" data-dc-action="ack"></button>'];
    case 'C-02':return states.map((s,i)=>`<button type="button" class="btn primary ${i===1?'dc-over':i===2?'dc-down':''}" ${i===3?'disabled':''}>${i===3?'不可用':'继续'}</button>`);
    case 'C-03':return states.map((s,i)=>`<button type="button" class="tab ${i===1?'dc-over':i===2?'dc-down':i===3?'selected':''}" aria-pressed="${i===3}" ${i===4?'disabled':''}>防御</button>`);
    case 'C-04':return states.map((s,i)=>`<button type="button" class="iconbutton ${i===1?'dc-over':i===2?'dc-down':i===3?'selected':''}" aria-label="防御 ${esc(s)}" ${i===4?'disabled':''}>${icon('turret')}</button>`);
    case 'C-05':return ['<p>保护核心，保持运输畅通。</p>','<h2 class="dc-heading">Mindustry</h2>','<p class="note">下一波将在 38 秒后到来。</p>','<p class="error">铜不足，还需要 25。</p>','<pre class="code">read value cell1 0\nprint value</pre>'];
    case 'C-06':return [dcField('云海工坊','aria-label="默认输入"')+'<textarea class="field dc-multiline" aria-label="多行说明" rows="2">说明支持多行输入。</textarea>','<input class="field dc-focused" aria-label="焦点输入" value="云海工坊">','<div class="field dc-focused dc-selection" role="textbox" aria-label="已选择文本" contenteditable="true"><mark>云海</mark>工坊</div>','<div class="field dc-focused dc-caret-field" role="textbox" aria-label="插入光标" contenteditable="true">云海<span class="dc-caret" aria-hidden="true"></span>工坊</div>',dcField('不可编辑','disabled aria-label="禁用输入"'),'<input class="field invalid" type="number" value="0" min="1" aria-invalid="true" aria-label="无效数量"><small class="error">数量至少为 1</small>'];
    case 'C-07':return [control('显示格线',toggle(false)),control('显示格线',toggle(true)),control('显示格线',toggle(false,true))];
    case 'C-08':return ['<div class="dc-track-only" aria-label="空滑条轨道"></div>','<div class="dc-range">'+range(35)+'</div>','<div class="dc-range dc-range-over">'+range(65)+'</div>','<div class="dc-range">'+range(80)+'</div><small>拖动后数值同步变化</small>'];
    case 'C-09':return ['vertical','horizontal','thin','none'].map(t=>`<div class="dc-scroll-shell dc-scroll-shell-${t}"><div class="dc-scroll dc-scroll-${t}" tabindex="0"><div>${Array.from({length:t==='horizontal'?6:12},(_,n)=>`<p>资源 ${n+1}　铜 ${120+n*20}</p>`).join('')}</div></div>${t==='none'?'':'<div class="dc-scroll-rail" aria-hidden="true"><i></i></div>'}</div>`);
    case 'C-10':return [row('基础生产线','铜 120 · 3×8','blueprint'),row('基础生产线','当前选中','blueprint',badge('选中'),true),'<div class="dc-disabled" aria-disabled="true">'+row('基础生产线','条件不满足','blueprint',badge('不可用','muted'))+'</div>',dcEmpty('暂无资源卡'),row('损坏存档','无法读取，请重新导入','save',badge('错误','danger'))];
    case 'C-11':return ['locked','available','active','complete','link'].map((s,i)=>s==='link'?'<div class="dc-node-link"><span>钻头</span><i></i><span>运输</span></div>':`<div class="node dc-node ${s==='locked'?'locked':s==='active'?'active':''}">${icon('research')}<b>${['🔒 未解锁','可研究','当前选中','✓ 已完成'][i]}</b>${i===3?badge('已解锁'):''}</div>`);
    case 'C-12':return [dcStack(stat('满','100 / 100'),bar(100),stat('部分','65 / 100'),bar(65),stat('空','0 / 100'),bar(0)),dcStack(stat('铜增加','1,240 ↑ +120'),bar(82),'<div class="error">铅减少　860 ↓ −45</div>'+bar(57)),dcStack(dcNotice('核心生命过低 · 20%',true),bar(20,true),'<div class="dc-warning-stripes">请立即修复防线</div>')];
    case 'C-13':return [dcStack(stat('铜','120 / 75'),badge('✓ 满足')),dcStack('<div class="error">铜 24 / 75</div>',badge('缺少 51','danger')),dcStack(control('铜方案',toggle(true)),control('铅方案',toggle(false)),dcNotice('任选一种材料满足需求')),`<div class="dc-inline">${icon('drill')}<strong class="dc-quantity">1,240</strong></div>`];
    case 'C-14':return ['<div class="dc-tooltip">机械钻头：开采矿物<span></span></div>','<div class="dc-toast">✓ 蓝图已保存</div>','<div class="dc-fade-sample">游戏已保存</div>','<div class="hint"><strong>第 1 / 3 步</strong><p>从铜矿附近开始建造。</p>'+dcButton('下一步','small')+'</div>',dcNotice('⚠ 核心正在受到攻击！',true)];
    case 'C-15':return [dcMap(),dcMap('expanded'),dcMap('markers')];
    case 'C-16':return ['<div class="loading" aria-label="加载中"></div><span>正在载入地图…</span>','<div class="loading"></div>'+dcButton('取消加载','','cancel-loading'),'<div class="dc-fade-sample">✓ 保存完成</div><small>淡出中间态</small>'];
    case 'C-17':return ['drill','export','turret','settings','drone'].map((x,i)=>`<div class="dc-world-marker dc-world-marker-${i}">${icon(x)}<span>${['⛏','↓','＋','+','✓'][i]}</span></div>`);
    case 'C-18':return [`<button class="iconbutton dc-touch" aria-label="未按">${icon('drone')}</button>`,`<button class="iconbutton dc-touch dc-down" aria-label="按下">${icon('turret')}</button>`,`<button class="iconbutton dc-touch selected" aria-label="选中">${icon('drone')}</button>`,`<div class="dc-inline"><button class="iconbutton dc-touch" aria-label="可用">${icon('play')}</button><button class="iconbutton dc-touch" aria-label="不可用" disabled>${icon('play')}</button></div>`];
    case 'C-19':return ['<pre class="code">&gt; print(60)\n60</pre><input class="field" aria-label="控制台输入" placeholder="输入命令（仅预览）">','<pre class="code"><span class="err">Error: invalid input</span>\nline 1: unknown identifier</pre>','<pre class="code">FPS       60\nMemory    240 MB\nUnits     24\nDraw calls 18</pre>'];
    case 'C-20':return [`<div class="dc-map dc-grid-on" data-dc-grid></div>${dcButton('切换格线','small','grid')}`,`<div class="dc-map dc-pan-map"></div><div class="dc-inline">${dcButton('−','small','zoom-out')}<output data-dc-zoom>100%</output>${dcButton('+','small','zoom-in')}</div>`,`<div class="dc-map"><div class="mapSelection"></div></div>`,`<div class="dc-inline"><button class="iconbutton selected" aria-label="钻头工具已选">${icon('drill')}</button><button class="iconbutton" aria-label="橡皮">${icon('close')}</button></div>`,dcStack(control('画笔大小',dcNumber(3,1,20)),control('旋转',options(['0°','90°','180°','270°'])))];
    default:return states.map(s=>dcNotice(s));
  }
}

function enhanceDialogComponent() {
  const viewport=document.querySelector('#gameViewport');
  viewport.classList.toggle('dc-preview',group.kind==='dialog'||group.kind==='component');
  if(group.kind!=='dialog'&&group.kind!=='component') return;
  if(group.kind==='dialog') viewport.innerHTML=dcDialogVariant();
  else {
    const examples=dcComponentExamples();
    const title=({'C-01':'窗口、标题与框板','C-05':'文字、数字与代码','C-20':'编辑器画布与工具'})[currentId]||group.name;
    viewport.innerHTML=windowFrame(title,`<div class="componentboard dc-board">${group.requiredDesignStates.map((s,i)=>`<section class="componentcell" data-dc-state="${i}"><span class="label">${esc(s)}</span>${examples[i]||''}</section>`).join('')}</div>`,btn('返回','','nav:UI-001'));
  }
  const frame=viewport.querySelector('.window');
  frame.dataset.dcGroup=currentId;frame.dataset.dcState=stateIndex;
  frame.querySelector('.screenBody').setAttribute('tabindex','0');
  frame.querySelectorAll('.dc-scroll-shell').forEach(shell=>{const scroller=shell.querySelector('.dc-scroll'),thumb=shell.querySelector('.dc-scroll-rail i');if(!thumb)return;scroller.addEventListener('scroll',()=>{const horizontal=shell.classList.contains('dc-scroll-shell-horizontal');const max=horizontal?scroller.scrollWidth-scroller.clientWidth:scroller.scrollHeight-scroller.clientHeight;const ratio=max?((horizontal?scroller.scrollLeft:scroller.scrollTop)/max):0;thumb.style[horizontal?'left':'top']=(ratio*65)+'%';});});
}

document.addEventListener('click',event=>{
  const choice=event.target.closest('[data-dc-choice]');
  if(choice){choice.parentElement.querySelectorAll('[data-dc-choice]').forEach(e=>{e.classList.toggle('selected',e===choice);e.setAttribute('aria-pressed',String(e===choice));});return;}
  const target=event.target.closest('[data-dc-action]');if(!target)return;
  event.preventDefault();event.stopPropagation();
  const action=target.dataset.dcAction,scope=target.closest('.window'),cell=target.closest('.componentcell')||scope;
  if(action==='check-all'||action==='check-none'){scope.querySelectorAll('.dc-ban-grid input').forEach(e=>e.checked=action==='check-all');const text=target.parentElement.querySelector('span');if(text)text.textContent=action==='check-all'?'当前选中 4 项':'当前选中 0 项';}
  else if(action==='effect'){const stage=scope.querySelector('.dc-effect-stage');stage.classList.add('dc-effect-playing');stage.querySelector('.dc-effect-caption').textContent='正在预览：'+target.closest('.row').querySelector('strong').textContent;}
  else if(action==='cancel-loading'){cell.querySelector('.loading')?.remove();target.replaceWith(Object.assign(document.createElement('span'),{textContent:'加载已取消'}));}
  else if(action==='grid'){cell.querySelector('[data-dc-grid]').classList.toggle('dc-grid-on');}
  else if(action.startsWith('zoom-')){const out=cell.querySelector('[data-dc-zoom]');const value=Math.max(50,Math.min(200,parseInt(out.textContent)+(action==='zoom-in'?25:-25)));out.textContent=value+'%';cell.querySelector('.dc-map').style.backgroundSize=value+'%';}
  else toast(action==='copy-preview'?'已选中错误详情（预览）':action==='file-preview'?'文件操作预览，未读写本地文件':/host|launch|reconnect|room/.test(action)?'交互预览，未连接游戏服务':'预览操作已确认');
},true);
