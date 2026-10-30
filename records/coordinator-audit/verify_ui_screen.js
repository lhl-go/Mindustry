const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'..','..'),sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const selected=process.argv[2]||'screen';
const filters=process.argv.slice(3);
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const page=await browser.newPage({viewport:{width:1366,height:768},deviceScaleFactor:1});
 const errors=[];let active='';page.on('pageerror',e=>errors.push({active,message:String(e)}));
 await page.goto('http://127.0.0.1:8765/ui/preview/?capture=1');
 const groups=await page.evaluate(()=>window.ART_DATA.groups);
 const targets=groups.filter(g=>(selected==='all'||g.kind===selected)&&(filters.length===0||filters.includes(g.id)));
 const sourcePaths=['ui/preview/index.html','ui/preview/data.js','ui/preview/preview.js','ui/preview/preview.css','ui/preview/screen-variants.js','ui/preview/screen-variants.css','ui/preview/dialog-component-variants.js','ui/preview/dialog-component-variants.css','ui/preview/screen-audit-fixes.js','ui/preview/screen-audit-fixes.css','ui/preview/unit-art.js','ui/preview/unit-art-data.js'].filter(f=>fs.existsSync(path.join(root,f)));
 const rasterFiles=await page.evaluate(()=>[...new Set((window.UNIT_ART_DATA||[]).map(u=>u.file))]);
 const kit=JSON.parse(fs.readFileSync(path.join(root,'ui/kit/manifest.json'),'utf8'));
 sourcePaths.push('ui/kit/manifest.json','characters/02-alchemy-engineer-clean.png',...kit.assets.map(a=>a.file),...rasterFiles);
 const sources=sourcePaths.map(file=>({file,sha256:sha(path.join(root,file))}));
 const records=[];
 fs.mkdirSync(path.join(root,'ui/states'),{recursive:true});
 for(const g of targets){
  for(const device of ['desktop','mobile']){
   const [width,height]=device==='desktop'?[1366,768]:[844,390];await page.setViewportSize({width,height});
   for(let i=0;i<g.requiredDesignStates.length;i++){
    active=g.id+'/'+i+'/'+device;
    const query=`?capture=1&id=${g.id}&state=${i}&device=${device}`;
    await page.goto('http://127.0.0.1:8765/ui/preview/'+query);
    await page.waitForFunction(()=>window.__artReady);await page.evaluate(()=>document.fonts.ready);
    const checks=await page.evaluate(()=>({ready:window.__artReady,images:[...document.images].filter(x=>!x.complete||!x.naturalWidth).map(x=>x.getAttribute('src')),view:[document.querySelector('#gameViewport').clientWidth,document.querySelector('#gameViewport').clientHeight],rootOverflow:[document.documentElement.scrollWidth>innerWidth,document.documentElement.scrollHeight>innerHeight],visibleTextLength:document.querySelector('#gameViewport').innerText.length,contentScroll:[...document.querySelectorAll('.screenBody,.column,.subpane')].filter(x=>x.scrollHeight>x.clientHeight+3).map(x=>({class:x.className,client:x.clientHeight,scroll:x.scrollHeight,overflow:getComputedStyle(x).overflowY})),outsideControls:[...document.querySelectorAll('#gameViewport button,#gameViewport input,#gameViewport select')].filter(x=>{const r=x.getBoundingClientRect();if(!r.width||!r.height)return false;let p=x.parentElement;while(p&&p.id!=='gameViewport'){if(['auto','scroll'].includes(getComputedStyle(p).overflowY)||['auto','scroll'].includes(getComputedStyle(p).overflowX))return false;p=p.parentElement;}return r.bottom>innerHeight+2||r.right>innerWidth+2||r.left < -2||r.top < -2;}).map(x=>({text:x.textContent.slice(0,35),class:x.className}))}));
    let file=null,hash=null;
    file=`ui/states/${g.id}--s${String(i).padStart(2,'0')}--${device}.png`;await page.screenshot({path:path.join(root,file),animations:'disabled'});hash=sha(path.join(root,file));
    records.push({group:g.id,stateIndex:i,state:g.requiredDesignStates[i],device,width,height,query,file,sha256:hash,checks});
   }
  }
  console.log(g.id,g.requiredDesignStates.length+' states');
 }
 const report={createdAt:new Date().toISOString(),selected,filters,renderer:'Chromium '+browser.version(),operation:'Native HTML text and controls rendered over source raster artwork; not AI generation or native-image upscaling.',runtimeIntegrationVerified:false,sources,records,errors};
 const name=selected+(filters.length?'-'+filters.join('-'):'');
 fs.writeFileSync(path.join(root,'records','coordinator-audit','ui-screen-validation.json'),JSON.stringify(report,null,2));
 console.log(JSON.stringify({records:records.length,errors,brokenImages:records.filter(r=>r.checks.images.length).map(r=>r.query),outside:records.filter(r=>r.checks.outsideControls.length).map(r=>({query:r.query,controls:r.checks.outsideControls}))}));
 await browser.close();
})();

