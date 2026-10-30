function enhanceUnitArt(){
 const units=window.UNIT_ART_DATA||[];
 const find=name=>units.find(u=>[u.id,u.name].some(n=>name===n||name.startsWith(n+' ·')||name.startsWith(n+'编队')||name.startsWith(n+' →')));
 document.querySelectorAll('#gameViewport .row,#gameViewport .card,#gameViewport .node,#gameViewport .hudUnit').forEach(el=>{
  const label=el.querySelector('strong,b,h3')?.textContent.trim()||'';
  let u=find(label);
  if(el.classList.contains('hudUnit')&&label==='建造单位')u=units.find(x=>x.id==='alpha');
  const im=el.querySelector('img');
  if(u&&im){im.src='../../'+u.file;im.alt=u.name;im.dataset.unitId=u.id;}
 });
}
