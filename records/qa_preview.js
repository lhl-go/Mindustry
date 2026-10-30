const {chromium}=require('playwright');
const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const page=await browser.newPage({viewport:{width:1366,height:768},deviceScaleFactor:1});
 let errors=[];page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 const ids=process.argv.slice(2).length?process.argv.slice(2):['UI-001','UI-002','UI-007','UI-015','UI-018','D-01','C-01'];
 fs.mkdirSync(path.join(root,'records','preview-qa'),{recursive:true});
 for(const id of ids){
  await page.goto('http://127.0.0.1:8765/ui/preview/?capture=1&id='+id);
  await page.waitForFunction(()=>window.__artReady);
  await page.evaluate(()=>document.fonts.ready);await page.screenshot({path:path.join(root,'records','preview-qa',id+'.png')});
  console.log(id,JSON.stringify(await page.evaluate(()=>({ready:window.__artReady,images:[...document.images].filter(x=>!x.complete||!x.naturalWidth).map(x=>x.src),scroll:[document.documentElement.scrollWidth,document.documentElement.scrollHeight]}))));
 }
 console.log('ERRORS',errors);await browser.close();
})();
