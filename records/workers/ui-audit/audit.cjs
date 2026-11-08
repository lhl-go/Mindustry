const fs=require('fs');
const path=require('path');
const crypto=require('crypto');
const {chromium}=require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root='D:/work/image/mindustry-image';
const output=path.join(root,'records/workers/ui-audit');
const captures=new Set(['desktop:D-07:2','desktop:C-06:0','desktop:C-12:0','desktop:C-15:0','mobile:D-03:1','mobile:D-07:3','mobile:D-11:3','mobile:D-12:3','mobile:C-06:0','mobile:C-12:0','mobile:C-15:0','mobile:D-16:1']);
(async()=>{
 fs.mkdirSync(path.join(output,'screenshots'),{recursive:true});
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const page=await browser.newPage({viewport:{width:1366,height:768},deviceScaleFactor:1});
 const errors=[],ignored=[];page.on('pageerror',e=>errors.push({type:'pageerror',message:e.message}));page.on('console',m=>{if(m.type()==='error'){const e={type:'console',message:m.text(),url:m.location().url};if(e.url.endsWith('/favicon.ico'))ignored.push(e);else errors.push(e);}});
 await page.goto('http://127.0.0.1:8765/ui/preview/?id=D-01&capture=1',{waitUntil:'networkidle'});
 const groups=await page.evaluate(()=>window.ART_DATA.groups.filter(g=>g.kind!=='screen').map(g=>({id:g.id,kind:g.kind,states:g.requiredDesignStates})));
 const checks=[];
 for(const deviceName of ['desktop','mobile']){
  await page.setViewportSize(deviceName==='desktop'?{width:1366,height:768}:{width:844,height:390});
  for(const g of groups){
   for(let s=0;s<g.states.length;s++){
    await page.evaluate(({id,s,d})=>{currentId=id;stateIndex=s;device=d;render();},{id:g.id,s,d:deviceName});
    await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.querySelectorAll('#gameViewport img')].map(im=>im.complete?Promise.resolve():new Promise(r=>{im.onload=r;im.onerror=r})));});
    const result=await page.evaluate(()=>{
     const viewport=document.querySelector('#gameViewport'),frame=viewport.querySelector('.window'),body=frame.querySelector('.screenBody'),actions=frame.querySelector('.actions'),vr=viewport.getBoundingClientRect();
     const r=actions?.getBoundingClientRect();
     return {enhanced:viewport.classList.contains('dc-preview'),group:frame.dataset.dcGroup,state:+frame.dataset.dcState,bodyWidth:body.clientWidth,bodyScrollWidth:body.scrollWidth,bodyHeight:body.clientHeight,bodyScrollHeight:body.scrollHeight,footerInViewport:!!r&&r.top>=vr.top&&r.bottom<=vr.bottom&&r.left>=vr.left&&r.right<=vr.right,footerHasButtons:!!actions?.querySelector('button'),componentCells:body.querySelectorAll('.componentcell').length,missingImages:[...viewport.querySelectorAll('img')].filter(im=>!im.complete||!im.naturalWidth).map(im=>im.src),bodyMarkup:body.innerHTML};
    });
    const bodyHash=crypto.createHash('sha256').update(result.bodyMarkup).digest('hex');delete result.bodyMarkup;
    const record={device:deviceName,id:g.id,stateIndex:s,state:g.states[s],...result,bodyHash};
    record.passed=result.enhanced&&result.group===g.id&&result.state===s&&result.bodyScrollWidth<=result.bodyWidth+2&&result.bodyHeight>40&&result.footerInViewport&&result.footerHasButtons&&result.missingImages.length===0&&(g.kind!=='component'||result.componentCells===g.states.length);
    checks.push(record);
    if(s===0||captures.has(`${deviceName}:${g.id}:${s}`)||['D-06','D-08','D-14'].includes(g.id))await page.locator('#gameViewport').screenshot({path:path.join(output,'screenshots',`${g.id}-${s}-${deviceName}.png`),animations:'disabled'});
   }
  }
 }
 const duplicates=[];for(const d of ['desktop','mobile'])for(const g of groups.filter(x=>x.kind==='dialog')){const found=new Map;for(const c of checks.filter(c=>c.device===d&&c.id===g.id)){if(found.has(c.bodyHash))duplicates.push({device:d,id:g.id,states:[found.get(c.bodyHash),c.stateIndex]});found.set(c.bodyHash,c.stateIndex);}}
 const interactions=[];
 const set=async(id,s=0)=>page.evaluate(({id,s})=>{currentId=id;stateIndex=s;device='mobile';render();},{id,s});
 for(const [id,s] of [['D-03',1],['D-11',3],['C-06',0],['D-08',1]]){
  await set(id,s);const scrolled=await page.evaluate(()=>{const body=document.querySelector('.screenBody');body.scrollTop=body.scrollHeight;const bottom=body.getBoundingClientRect().bottom,footer=document.querySelector('.actions').getBoundingClientRect();return {needed:body.scrollHeight>body.clientHeight,atBottom:body.scrollTop+body.clientHeight>=body.scrollHeight-2,footerVisible:footer.top>=bottom&&footer.bottom<=390};});
  interactions.push({name:`${id} mobile scroll reaches end with fixed footer`,passed:scrolled.atBottom&&scrolled.footerVisible,...scrolled});
  await page.locator('#gameViewport').screenshot({path:path.join(output,'screenshots',`${id}-${s}-mobile-scrolled.png`),animations:'disabled'});
 }
 await set('D-15',2);await page.getByRole('button',{name:'清空',exact:true}).click();interactions.push({name:'D-15 clear all',passed:await page.locator('.dc-ban-grid input:checked').count()===0});await page.getByRole('button',{name:'全选',exact:true}).click();interactions.push({name:'D-15 select all',passed:await page.locator('.dc-ban-grid input:checked').count()===4});
 await set('D-16');await page.getByRole('button',{name:'播放',exact:true}).first().click();interactions.push({name:'D-16 local effect preview',passed:await page.locator('.dc-effect-playing').count()===1});
 await set('C-08');const slider=page.locator('.componentcell').nth(3).locator('input');await slider.fill('42');interactions.push({name:'C-08 range output',passed:await page.locator('.componentcell').nth(3).locator('output').textContent()==='42%'});
 await set('C-20');await page.getByRole('button',{name:'切换格线',exact:true}).click();interactions.push({name:'C-20 grid toggle',passed:await page.locator('.dc-grid-on').count()===0});
 const report={checkedAt:new Date().toISOString(),scope:'D-01..D-16 and C-01..C-20 only',viewportSizes:{desktop:[1366,768],mobile:[844,390]},checkedStateViewportPairs:checks.length,consoleErrors:errors,ignoredFaviconErrors:ignored,duplicateDialogBodies:duplicates,failed:checks.filter(c=>!c.passed),interactions,checks,limitations:['Browser art/DOM preview only; no Mindustry client integration or network/file side effects.','All states were rendered and geometry-checked; representative screenshots require separate visual review.']};
 fs.writeFileSync(path.join(output,'browser-audit.json'),JSON.stringify(report,null,2));
 console.log(JSON.stringify({checked:checks.length,failed:report.failed,errors,duplicates,interactions},null,2));
 await browser.close();
})().catch(e=>{console.error(e);process.exitCode=1});
