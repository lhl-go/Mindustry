/* Art-layout state extensions. No game, network or filesystem operations. */
function dynamicConfiguration(name){
 const itemPicker=()=>toolbar('搜索物品')+cards([['铜','drill','选中'],['铅','conveyor',''],['石墨','furnace',''],['硅','power',''],['钛','database',''],['钍','research','']],'three')+btn('取消选择','small','clear');
 const unitPicker=()=>cards([['尖刀','turret','地面'],['星辉','drone','空中'],['独影','drone','支援']],'three');
 const commands=()=>cards([['移动','play'],['修复','settings'],['辅助','drone'],['停止','pause']]);
 const blockPicker=()=>cards([['城墙','mods'],['双管炮','turret'],['电力节点','power']],'three');
 let content='';
 switch(name){
  case 'Accelerator':content=hint('储能与发射核心已就绪。')+stat('发射目标','其他星球')+btn('选择星球并发射','primary','nav:UI-005','planet');break;
  case 'LandingPad':content=itemPicker()+stat('进口速度','120 / 秒')+btn('重定向出口','small')+btn('选择来源区域','small','nav:UI-005');break;
  case 'LaunchPad':content=stat('当前目的地','区域 175')+btn('选择出口目的地','primary','nav:UI-005','export');break;
  case 'TargetDummy':content=control('敌方队伍',toggle(true))+control('飞行',toggle(false))+control('护甲',field('12','','number'))+control('重置时间（秒）',field('5','','number'))+control('碰撞尺寸（格）',field('2','','number'));break;
  case 'CanvasBlock':content=hint('修改画布中显示的像素图案。')+btn('编辑画布','primary','nav:UI-027','blueprint');break;
  case 'LogicBlock':content=stat('已连接建筑','3')+btn('编辑逻辑','primary','nav:UI-024','database');break;
  case 'MessageBlock':content='<textarea class="field" style="width:100%" maxlength="256">防线一号：优先供电\n补充弹药后继续向北扩建。</textarea>'+btn('编辑消息','small','modal:D-02');break;
  case 'LightBlock':content=control('灯光颜色','<input type="color" value="#7ec28e">')+btn('颜色选择','primary','modal:D-10');break;
  case 'Constructor':content=blockPicker();break;
  case 'PayloadRouter':case 'PayloadSource':content=tabs(['建筑','单位'])+blockPicker()+unitPicker();break;
  case 'LiquidSource':content=cards([['水','database'],['石油','furnace'],['冷冻液','power'],['矿渣','research']])+btn('取消选择','small','clear');break;
  case 'CoreBlock':content=hint('当前规则允许核心配置，可变更所属队伍。')+cards([['绿队','planet','当前'],['蓝队','planet'],['红队','planet'],['中立','planet']]);break;
  case 'Reconstructor':content=stat('单位','尖刀 → 战锤')+commands();break;
  case 'UnitFactory':content=unitPicker()+pane('默认指令',commands());break;
  default:content=itemPicker();
 }
 return windowFrame('建筑配置 · '+name,`<div class="content"><div class="column">${map()}</div><div class="column detail configuration">${content}</div></div>`,btn('取消')+btn('完成','primary'));
}
function statePanel(title,body){const side=document.querySelector('.column.detail')||document.querySelector('.column.narrow');if(side){side.insertAdjacentHTML('beforeend',pane(title,body));}else document.querySelector('.screenBody')?.insertAdjacentHTML('beforeend',pane(title,body));}
function stateDialog(title,body,actions=''){document.querySelector('#gameViewport').insertAdjacentHTML('beforeend',`<div class="stateOverlay">${windowFrame(title,body,actions||btn('取消')+btn('确认','primary'),'compact')}</div>`);}
function replaceBody(html){document.querySelector('.screenBody').innerHTML=html;}
function enhanceScreen(){
 if(group.kind!=='screen')return;
 const si=stateIndex, id=currentId, viewport=document.querySelector('#gameViewport');
 if(id==='UI-002'&&si>=6){viewport.innerHTML=dynamicConfiguration(state.split('：')[1]);return;}
 if(id==='UI-001'&&si===1){document.querySelector('.menuFine').textContent='移动端 · 触控操作';}
 if(id==='UI-002'){
  if(si===1)viewport.insertAdjacentHTML('beforeend','<div class="touchControls">'+btn('旋转','small')+btn('拆除','small')+btn('确认建造','small primary')+'</div>');
  if(si===2)document.querySelector('.hudUnit').insertAdjacentHTML('beforeend',hint('铅不足：24 / 45',true));
  if(si===3)document.querySelector('.hudPlate[style]')?.insertAdjacentHTML('beforeend',stat('库存','铜 120 / 300')+stat('生产进度','65%')+bar(65));
  if(si===4)document.querySelector('.hudTop').insertAdjacentHTML('afterend','<div class="waveDetails">'+pane('下一波 · 12',stat('尖刀','24')+stat('战锤','8')+stat('星辉','6')+btn('立即开始','small primary'))+'</div>');
  if(si===5)document.querySelector('.hudWarning').insertAdjacentHTML('afterend','<div class="waitBanner">游戏已暂停 · 等待其他玩家就绪</div>');
 }
 if(id==='UI-003'){
  const u=document.querySelector('.hudUnit');
  if(si===0){u.innerHTML=hint('尚未选中单位。框选或点击友方单位。');document.querySelectorAll('.hudBuild .card').forEach(x=>x.disabled=true);}
  if(si===1)u.innerHTML=icon('turret','big')+stat('尖刀编队','6 个')+stat('生命','900 / 900')+bar(100);
  if(si===2)u.innerHTML=stat('尖刀','6')+stat('星辉','4')+stat('独影','2')+badge('混合编队 · 12 个');
  if(si===3)document.querySelector('.hudBuild').insertAdjacentHTML('beforeend',hint('移动指令已选中 · 点击目标位置'));
  if(si===4)document.querySelector('.hudBuild').innerHTML=tabs(['攻击','保持位置','跟随','自动修复'],1)+cards([['攻击','turret','主动交战'],['保持位置','pause','已选'],['跟随','drone','跟随目标'],['修复','settings','自动辅助']]);
 }
 if(id==='UI-004'&&si===0){viewport.innerHTML=hud();}
 if(id==='UI-005'){
  if(si===1)statePanel('发射状态',badge('可发射')+badge('锁定','muted')+btn('继续当前区域','small primary')+hint('锁定区域需要先占领前置区域。'));
  if(si===2)statePanel('区域状态',hint('区域 175 正受到攻击！',true)+stat('前线区域','已占领')+stat('后方区域','已失守'));
  if(si===3)statePanel('全局覆盖',stat('已占领区域','12')+stat('资源产量','铜 240 / 分')+control('显示资源',toggle(true))+control('显示威胁',toggle(true)));
 }
 if(id==='UI-006'){
  if(si===1){document.querySelector('.column.detail .btn').disabled=true;statePanel('未解锁',hint('需先完成机械钻头研究。'));}
  if(si===2)statePanel('资源不足',hint('铜 24 / 75 · 还需 51',true));
  if(si===3){document.querySelectorAll('.node')[1].classList.add('active');statePanel('研究进度',stat('传送带','已完成')+stat('电池','研究中')+bar(65));}
 }
 if(id==='UI-007'){
  if(si===1){document.querySelector('[data-search]').value='青云';document.querySelectorAll('.searchable .row').forEach((x,i)=>x.hidden=i>0);}
  if(si===4)statePanel('无法加入',hint('服务器版本 v159 与当前 v160.7 不兼容。',true));
  if(si===5)stateDialog('正在连接','<div class="loading"></div><p>正在连接到青云工坊…</p>'+hint('连接断开时可以尝试重新连接。'),btn('取消')+btn('重连','primary'));
  if(si===6)stateDialog('添加服务器',control('名称',field('青云工坊'))+control('地址',field('example.invalid:6567')));
 }
 if(id==='UI-008'){
  if(si===2)stateDialog('保存游戏',control('存档名称',field('云海工坊'))+hint('同名存档已存在。确认后将覆盖。',true),btn('取消')+btn('新建存档')+btn('覆盖','danger'));
  if(si===3)statePanel('存档管理',btn('导入存档','small','modal:D-11')+btn('导出存档','small'));
  if(si===4)statePanel('载入失败',hint('存档损坏或缺少依赖资源，无法读取。',true));
 }
 if(id==='UI-009'&&si===1)statePanel('筛选',control('模式',options(['全部','生存','PvP','沙盒']))+control('显示隐藏地图',toggle(false)));
 if(id==='UI-009'&&si===3)statePanel('开始对局',btn('自定义规则','small','nav:UI-020')+btn('选择队伍','small','modal:D-09')+control('敌人难度',options(['标准','挑战'])));
 if(id==='UI-011'&&si===2)statePanel('战役限制',hint('该内容需要在对应星球解锁。'));
 if(id==='UI-011'&&si===4)stateDialog('字段查看',stat('health','250')+stat('range','110')+stat('reload','20')+stat('size','1'));
 if(id==='UI-012'){
  if(si===3)stateDialog('编辑蓝图标签',field('生产, 基础','标签')+btn('添加标签','small')+btn('删除标签','small danger'));
  if(si===4)statePanel('导入与导出',btn('导入文件','small','modal:D-11')+btn('从剪贴板导入','small')+btn('导出文件','small')+btn('复制蓝图','small'));
 }
 if(id==='UI-013'&&si===1)document.querySelectorAll('input[type=checkbox]').forEach(x=>x.checked=false);
 if(id==='UI-013'&&si===3)statePanel('可用更新',stat('已安装','1.0')+stat('最新版本','1.1')+btn('更新','small primary'));
 if(id==='UI-013'&&si===4)statePanel('依赖错误',hint('缺少前置模组：机关基础包。部分内容无法载入。',true));
 if(id==='UI-014'&&si===0)statePanel('列表状态',hint('正在加载模组目录…')+btn('重试','small','refresh'));
 if(id==='UI-014'&&si===4)statePanel('下载状态',bar(45)+stat('进度','4.5 / 10 MB')+hint('网络中断。可取消或重试。',true)+btn('取消','small')+btn('重试','small'));
 if(id==='UI-016'&&si===2)document.querySelectorAll('[data-act=capture-key]')[4].textContent='T';
 if(id==='UI-016'&&si===4)stateDialog('重置按键',hint('将所选按键或所有按键恢复为默认绑定。'),btn('取消')+btn('单项重置')+btn('全部重置','danger'));
 if(id==='UI-017'){
  if(si===1)stateDialog('新建地图',control('名称',field('新地图'))+control('宽度',field('256','','number'))+control('高度',field('256','','number')));
  if(si===2)stateDialog('覆盖地图',hint('已存在同名地图，是否覆盖？',true),btn('取消')+btn('另存为')+btn('覆盖','danger'));
  if(si===3)stateDialog('地图信息',control('名称',field('云海工坊'))+control('作者',field('青云'))+'<textarea class="field">合作生存工坊。</textarea>');
  if(si===4)stateDialog('删除地图',hint('确定删除“云海工坊”？此操作不可恢复。',true),btn('取消')+btn('导出备份')+btn('删除','danger'));
 }
 if(id==='UI-018'){
  const p=document.querySelector('.editorProperties');
  if(si===1)p.innerHTML='<h4>可见图层</h4>'+control('地表',toggle())+control('地形',toggle())+control('建筑',toggle())+control('标记',toggle());
  if(si===2)p.innerHTML='<h4>队伍</h4>'+cards([['绿队','planet'],['蓝队','planet'],['红队','planet']],'three');
  if(si===3)p.innerHTML='<h4>建筑参数</h4>'+control('建筑',options(['炮塔','钻头','核心']))+control('队伍',options(['绿队','红队']))+control('旋转',options(['0°','90°','180°','270°']))+btn('详细配置','small','nav:UI-002');
  if(si===4)p.innerHTML='<h4>画笔</h4>'+control('大小',field('5','','number'))+control('形状',options(['圆形','方形']))+control('旋转',options(['0°','90°','180°','270°']));
  if(si===5)stateDialog('未保存的更改',hint('地图有未保存的更改，返回前是否保存？'),btn('取消')+btn('放弃','danger')+btn('保存','primary'));
 }
 if(id==='UI-019'&&si===1)statePanel('滤镜操作',btn('新增','small')+btn('向上','small')+btn('向下','small')+btn('复制','small')+btn('删除','small danger'));
 if(id==='UI-019'&&si===4)statePanel('生成参数',btn('复制参数','small')+btn('粘贴参数','small')+btn('重置','small danger'));
 if(id==='UI-020'&&si===5){document.querySelector('[data-search]').value='单位';replaceBody(toolbar('搜索规则')+pane('搜索结果',control('单位上限',field('24','','number'))+control('单位生命倍率',field('1.0','','number'))+control('单位伤害倍率',field('1.0','','number'))));}
 if(id==='UI-021'&&si===2)statePanel('单位组筛选',control('单位',options(['全部','尖刀','战锤','星辉']))+control('排序',options(['起始波次','数量','单位'])));
 if(id==='UI-021'&&si===4)statePanel('预览',stat('第 10 波','尖刀 24 · 星辉 6')+control('起始波次',field('10','','number'))+control('出生点',options(['全部','北侧','东侧'])));
 if(id==='UI-022'&&si===1)stateDialog('新增目标',control('类型',options(['收集物品','建造建筑','击败单位','到达波次']))+control('名称',field('新的目标')));
 if(id==='UI-022'&&si===3)statePanel('标记参数',control('形状',options(['圆形','文本','箭头','区域']))+control('X / Y',field('128, 64'))+control('标签',field('防御区域'))+control('颜色','<input type="color" value="#d4ac55">'));
 if(id==='UI-022'&&si===4)statePanel('目标管理',btn('复制','small')+btn('粘贴','small')+btn('清空目标','small danger','modal:D-01'));
 if(id==='UI-023'&&si===4)statePanel('逻辑',btn('编辑程序','primary','nav:UI-024','database'));
 if(id==='UI-024'){
  if(si===1)stateDialog('添加指令',toolbar('搜索指令')+rows([['读取','输入 / 输出','database'],['绘制','图像','blueprint'],['运算','数值','research'],['跳转','流程控制','play']]));
  if(si===2)stateDialog('编辑读取指令',control('输出变量',field('value'))+control('存储器',field('cell1'))+control('地址',field('0','','number'))+btn('删除指令','small danger'));
  if(si===4)statePanel('程序管理',btn('导入文本','small')+btn('导出文本','small')+btn('复制代码','small')+btn('清空程序','small danger','modal:D-01'));
 }
 if(id==='UI-025'&&si===4)statePanel('文本工具',btn('插入图标','small','modal:D-09')+btn('恢复原文','small')+btn('复制属性','small'));
 if(id==='UI-026'&&si===2)stateDialog('资源 ZIP',btn('导入 ZIP','','modal:D-11')+btn('导出 ZIP')+hint('同名资源将提示覆盖。'));
 if(id==='UI-026'&&si===4)stateDialog('清空资源',hint('将移除地图内全部自定义资源。',true),btn('取消')+btn('清空','danger'));
 if(id==='UI-026'&&si>=5){
  const type=state.split('：')[1],details=document.querySelector('.column.detail');
  document.querySelector('.tabs').outerHTML=tabs(['图片','音效','音乐','文本','内容','补丁'],si-5);
  if(type==='音效'||type==='音乐')details.innerHTML='<h3>'+type+'属性</h3>'+control('名称',field(type==='音乐'?'workshop-theme':'core-warning'))+control('音量',range(65))+control('循环播放',toggle(type==='音乐'))+btn('播放','small','','play')+btn('暂停','small','','pause')+btn('导出','small')+btn('删除','small danger','modal:D-01');
  if(type==='文本')details.innerHTML='<h3>语言文本</h3>'+stat('语言','简体中文')+stat('属性数量','3')+btn('编辑语言与属性','primary','nav:UI-025')+btn('导入','small')+btn('导出','small');
  if(type==='内容')details.innerHTML='<h3>自定义内容</h3>'+control('内部名称',field('jade-turret'))+control('类型',options(['建筑','单位','物品','液体','星球','天气','状态']))+'<textarea class="field">{\n  "health": 250,\n  "size": 1\n}</textarea>'+btn('重新加载','small','refresh')+btn('从剪贴板导入','small')+btn('导出','small');
  if(type==='补丁')details.innerHTML='<h3>内容补丁</h3>'+control('名称',field('defense-balance'))+stat('修改字段','2')+'<textarea class="field">{\n  "blocks.duo.health": 250\n}</textarea>'+btn('复制','small')+btn('重载','small','refresh')+btn('移除','small danger','modal:D-01');
  const list=document.querySelector('.searchable');list.innerHTML=row(type==='音乐'?'workshop-theme.ogg':type==='音效'?'core-warning.ogg':type==='图片'?'banner.png':type==='文本'?'bundle_zh_CN.properties':type==='内容'?'jade-turret.hjson':'defense-balance.json','本地图资源 · '+type,type==='图片'?'blueprint':'database',badge('可用'),true);
 }
 if(id==='UI-027'&&si===2)statePanel('图像导入导出',btn('导入 PNG','small','modal:D-11')+btn('导出 PNG','small'));
 if(id==='UI-028'&&si===3)stateDialog('投票踢出',control('玩家',field('玩家 02'))+control('理由',field('请填写理由'))+hint('需要其他玩家投票通过。'),btn('取消')+btn('发起投票','danger'));
 if(id==='UI-028'&&si===4)stateDialog('选择队伍',cards([['绿队','planet'],['蓝队','planet'],['红队','planet']],'three'));
 if(flags.error&&['UI-006','UI-008','UI-023'].includes(id))document.querySelectorAll('.actions .primary,.column.detail>.primary').forEach(x=>x.disabled=true);
}
document.addEventListener('click',event=>{
 const tab=event.target.closest('[data-tab]'),rowEl=event.target.closest('[data-select]');
 if(currentId==='UI-015'&&rowEl?.closest('.column.narrow')){event.stopImmediatePropagation();stateIndex=[...rowEl.parentElement.children].indexOf(rowEl);render();return;}
 if(tab&&['UI-020','UI-026'].includes(currentId)){event.stopImmediatePropagation();stateIndex=+tab.dataset.tab+(currentId==='UI-026'?5:0);render();return;}
 if(tab&&currentId==='UI-002'&&stateIndex===0&&tab.closest('.hudBuild')){
  const choices=[ [['机械钻头','drill','铜 12'],['气动钻头','drill','铜 18'],['激光钻头','power','硅 30']], [['传送带','conveyor','铜 1'],['路由器','conveyor','铜 3'],['分配器','conveyor','铜 3'],['桥接带','conveyor','铜 6']], [['石墨压缩机','furnace','铜 75'],['硅冶炼厂','furnace','铜 30'],['窑炉','furnace','铅 30']], [['电力节点','power','铜 1'],['电池','power','铅 20'],['燃烧发电机','power','铜 25']], [['炮塔','turret','铜 35'],['城墙','mods','铜 6'],['修复器','settings','铜 25'],['护盾','power','硅 50'],['大型城墙','mods','铜 24'],['散射炮','turret','铅 45']], [['地面工厂','drone','铜 50'],['空军工厂','drone','铅 120'],['海军工厂','drone','铜 150']] ];
  document.querySelector('.hudBuild .grid').outerHTML=cards(choices[+tab.dataset.tab]);
 }
},true);
