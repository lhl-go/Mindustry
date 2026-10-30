const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];
 page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('file:///'+path.join(__dirname,'index.html').replaceAll('\\','/'));
 const settle=()=>page.evaluate(async()=>{document.querySelectorAll('#grid img').forEach(i=>i.loading='eager');await Promise.all([...document.querySelectorAll('#grid img')].map(i=>i.decode().catch(()=>{})));return[...document.querySelectorAll('#grid img')].filter(i=>!i.naturalWidth).map(i=>i.getAttribute('src'))});
 let broken=await settle();const cards=await page.locator('.card').count();
 fs.mkdirSync(path.join(__dirname,'qa'),{recursive:true});await page.screenshot({path:path.join(__dirname,'qa/gallery-desktop.png')});
 await page.locator('#domain').selectOption('root-turrets');const filtered=await page.locator('#counter').innerText();
 await page.locator('#q').fill('malign');const searched=await page.locator('.card').count();
 await page.locator('#native').click();broken.push(...await settle());await page.locator('#bg').click();
 await page.locator('#grid img').first().click();const zoom=await page.locator('#zoom').evaluate(e=>e.open);await page.locator('#close').click();
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(__dirname,'qa/gallery-mobile.png')});
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
 const passed=errors.length===0&&broken.length===0&&cards===96&&filtered.includes('145')&&searched>0&&zoom&&!overflow;
 const result={checkedAt:new Date().toISOString(),passed,errors,broken,cards,filtered,searched,zoom,mobileOverflow:overflow,scope:'Offline pagination, domain/search filters, native toggle, dark background, image modal and mobile layout; rendered first page and turret search.',sources:['full-game/index.html','full-game/coverage.json'].map(file=>({file,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,file))).digest('hex')}))};
 fs.writeFileSync(path.join(__dirname,'qa/gallery-review.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));await browser.close();if(!passed)process.exitCode=1;
})();
