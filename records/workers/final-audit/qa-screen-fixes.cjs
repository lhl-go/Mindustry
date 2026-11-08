const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {chromium}=require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const out='D:/work/image/mindustry-image/records/workers/final-audit';
const save=new Set(['UI-004:2:mobile','UI-011:2:mobile','UI-014:1:desktop','UI-014:3:mobile','UI-018:2:mobile','UI-018:3:mobile','UI-019:3:desktop','UI-021:2:mobile','UI-021:3:desktop','UI-022:3:mobile','UI-023:3:mobile','UI-025:3:mobile','UI-026:1:mobile','UI-027:1:mobile','UI-027:2:mobile','UI-028:1:mobile']);
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});const page=await browser.newPage({viewport:{width:1366,height:768},deviceScaleFactor:1});const errors=[];
 page.on('pageerror',e=>errors.push({message:e.message}));page.on('console',m=>{if(m.type()==='error'&&!m.location().url.endsWith('/favicon.ico'))errors.push({message:m.text(),url:m.location().url});});
 await page.goto('http://127.0.0.1:8765/ui/preview/?id=UI-014&state=1&capture=1',{waitUntil:'networkidle'});
 const gs=await page.evaluate(()=>window.ART_DATA.groups.filter(g=>SA_AFFECTED_IDS.includes(g.id)).map(g=>({id:g.id,states:g.requiredDesignStates})));
 const checks=[];fs.mkdirSync(path.join(out,'screenshots'),{recursive:true});
 for(const d of ['desktop','mobile']){
  await page.setViewportSize(d==='desktop'?{width:1366,height:768}:{width:844,height:390});
  for(const g of gs)for(let i=0;i<g.states.length;i++){
   await page.evaluate(({id,i,d})=>{currentId=id;stateIndex=i;device=d;render();},{id:g.id,i,d});
   await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.querySelectorAll('#gameViewport img')].map(im=>im.complete?Promise.resolve():new Promise(r=>{im.onload=r;im.onerror=r})));});
   const check=await page.evaluate(()=>{const v=document.querySelector('#gameViewport'),b=v.querySelector('.screenBody'),r=v.getBoundingClientRect(),f=v.querySelector('.actions')?.getBoundingClientRect();return {auditHook:v.dataset.auditState,bodyOverflow:b?b.scrollWidth>b.clientWidth+2:false,bodyHeight:b?.clientHeight,footerVisible:!f||(f.top>=r.top&&f.bottom<=r.bottom),badImages:[...v.querySelectorAll('img')].filter(im=>!im.complete||!im.naturalWidth).map(im=>im.src),stateText:v.innerText};});
   const buf=await page.locator('#gameViewport').screenshot({animations:'disabled'}),hash=crypto.createHash('sha256').update(buf).digest('hex');
   if(save.has(`${g.id}:${i}:${d}`))fs.writeFileSync(path.join(out,'screenshots',`${g.id}-${i}-${d}.png`),buf);
   checks.push({id:g.id,stateIndex:i,state:g.states[i],device:d,...check,sha256:hash,passed:check.auditHook===`${g.id}:${i}`&&!check.bodyOverflow&&check.footerVisible&&check.badImages.length===0});
  }
 }
 const duplicateStates=[];for(const d of ['desktop','mobile'])for(const g of gs){const map=new Map;for(const c of checks.filter(x=>x.id===g.id&&x.device===d)){if(map.has(c.sha256))duplicateStates.push({id:g.id,device:d,states:[map.get(c.sha256),c.stateIndex]});map.set(c.sha256,c.stateIndex);}}
 const offlineErrors=[];const offline=await browser.newPage({viewport:{width:1440,height:900}});offline.on('pageerror',e=>offlineErrors.push(e.message));offline.on('console',m=>{if(m.type()==='error')offlineErrors.push(m.text())});
 await offline.goto('file:///D:/work/image/mindustry-image/exports/index.html',{waitUntil:'load'});await offline.waitForFunction(()=>window.DELIVERY_DATA&&document.querySelectorAll('#summary article').length===4);
 await offline.locator('button[data-tab="units"]').click();await offline.locator('#unitSearch').fill('gamma');const gamma=await offline.locator('#unitGrid').innerText();
 await offline.locator('button[data-tab="ui"]').click();const frame=offline.frames().find(f=>f.url().includes('/ui/preview/index.html'));await frame.waitForFunction(()=>window.__artReady);
 const offlineCheck={url:offline.url(),unitSearchGammaPresent:gamma.includes('gamma'),uiGroups:await frame.evaluate(()=>window.ART_DATA.groups.length),iframeReady:await frame.evaluate(()=>window.__artReady),consoleErrors:offlineErrors};
 const report={checkedAt:new Date().toISOString(),affectedIds:gs.map(g=>g.id),stateViewportPairs:checks.length,errors,failed:checks.filter(c=>!c.passed),duplicateStates,offlineCheck,checks};
 fs.writeFileSync(path.join(out,'screen-fixes-browser.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({count:checks.length,failed:report.failed,errors,duplicateStates,offlineCheck},null,2));await browser.close();
})().catch(e=>{console.error(e);process.exitCode=1});
