"""Integrate the accepted Chinese logo, preserving exact upstream source canvases."""
from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 logo=ROOT/'branding/tiangong-xianzhen/tiangong-xianzhen-logo.png';h=sha(logo)
 mpath=ROOT/'full-game/ui-system/manifest.json';m=json.loads(mpath.read_text(encoding='utf-8'))
 for a in m['assets']:
  if a['sourcePath']not in ['core/assets-raw/sprites/ui/logo.png','core/assets/sprites/logo.png']:continue
  p=ROOT/a['file'];size=a['sourceSize'];im=Image.open(logo);im.thumbnail(size,Image.Resampling.LANCZOS);out=Image.new('RGBA',size);out.paste(im,((size[0]-im.width)//2,(size[1]-im.height)//2));out.save(p)
  a['sha256']=sha(p);a['derivedFrom']=[{'file':logo.relative_to(ROOT).as_posix(),'sha256':h,'record':'branding/tiangong-xianzhen/tiangong-xianzhen-logo.png.generation.json'}]
  a['operation']={'kind':'contain_downsample','resampling':'LANCZOS','exactTitle':'天工仙阵','note':'Exact upstream source canvas. Runtime mod provides the larger aspect-correct title separately.'}
  (Path(str(p)+'.derived.json')).write_text(json.dumps({'file':a['file'],'sha256':a['sha256'],'derivedFrom':a['derivedFrom'],'operation':a['operation'],'width':size[0],'height':size[1],'actualModel':None,'actualQuality':None},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 mpath.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 for name in ['full-game/build_gallery.py','full-game/index.html','exports/index.html','ui/preview/index.html','ui/preview/preview.js','ui/preview/dialog-component-variants.js']:
  p=ROOT/name;s=p.read_text(encoding='utf-8')
  # Source authorship and official URLs remain identifiable; only displayed headings change.
  s=s.replace('<h2>Mindustry</h2>','<h2>天工仙阵</h2>').replace('<h1>Mindustry</h1>','<h1>天工仙阵</h1>').replace('<strong>Mindustry</strong>','<strong>天工仙阵</strong>').replace('关于 Mindustry','关于 天工仙阵').replace('<title>Mindustry','<title>天工仙阵').replace('<h1>Mindustry ·','<h1>天工仙阵 ·')
  if name=='ui/preview/preview.js':s=s.replace('<h2>天工仙阵</h2>','<img class="gameTitleLogo" src="../../branding/tiangong-xianzhen/tiangong-xianzhen-logo.png" alt="天工仙阵">',1)
  p.write_text(s,encoding='utf-8')
 p=ROOT/'ui/preview/preview.css';s=p.read_text(encoding='utf-8');s+='\n.gameTitleLogo{width:100%;max-width:500px;height:auto;object-fit:contain}\n';p.write_text(s,encoding='utf-8')
 p=ROOT/'README.md';s=p.read_text(encoding='utf-8');s=s.replace('# Mindustry · 道家 Q 版全量美术','# 天工仙阵 · 全量游戏美术',1);s+='\n正式游戏名为 **天工仙阵**，公开仓库名沿用 `Mindustry`。透明 Logo 与逐图记录见 [品牌素材](branding/tiangong-xianzhen/README.md)，可直接加载的美术模块及游戏内验收见 [接入说明](full-game/integration/README.md)。\n';p.write_text(s,encoding='utf-8')
 print('Brand title integrated into source mapping and live previews.')
if __name__=='__main__':main()
