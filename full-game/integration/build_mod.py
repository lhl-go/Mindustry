"""Package accepted art using Mindustry v160.7's supported sprites-override path."""
import json,hashlib,zipfile,subprocess,shutil,io,re,base64
from PIL import Image
import numpy as np
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 c=json.loads((ROOT/'full-game/coverage.json').read_text(encoding='utf-8'))
 rows=[];targets=set()
 for a in c['assets']:
  src=a['sourcePath'];marker='core/assets-raw/sprites/'
  if src.startswith(marker)and src.endswith('.png'):
   target='sprites-override/'+src[len(marker):]
  elif src.startswith('core/assets/')and not src.startswith('core/assets/sprites/'):
   target=src[len('core/assets/'):]
  else:continue
  if target in targets:raise ValueError(target)
  targets.add(target);rows.append({'file':a['file'],'target':target,'sha256':a['sha256']})
 units=json.loads((ROOT/'full-game/units/manifest.json').read_text())
 for a in units.get('additionalAtlasRegions',[])+units.get('generatedAtlasRegions',[]):
  if a.get('copyIntoSourceTree') or a in units.get('generatedAtlasRegions',[]):
   target=('extra-regions/'+a['id']+'.png')if a.get('copyIntoSourceTree')else'sprites-override/units/'+a['id']+'.png'
   rows.append({'file':a['file'],'target':target,'sha256':a['sha256']})
 work=ROOT/'.work/runtime-acceptance';jar=work/'Mindustry.jar';classes=work/'brand-classes';classes.mkdir(exist_ok=True)
 subprocess.run(['javac','-encoding','UTF-8','--release','17','-cp',str(jar),'-d',str(classes),str(HERE/'src/tiangong/BrandMod.java')],check=True)
 meta={'name':'tiangong-xianzhen-art','displayName':'天工仙阵 · 全量美术','author':'lhl-go','version':'1.0','minGameVersion':'160.7','main':'tiangong.BrandMod','java':True,'pregenerated':True,'description':'道家 Q 版全量图片与品牌美术。基于 Mindustry v160.7，来源与许可见随包说明。'}
 # Official ImageTileGenerator layout and algorithm: every raw 4x4 input becomes 47 runtime regions.
 generator=HERE/'upstream/ImageTileGenerator.java';code=generator.read_text(encoding='utf-8');layout=np.array(Image.open(io.BytesIO(base64.b64decode(re.search(r'Base64Coder.decode\("([A-Za-z0-9+/=]+)"',code)[1]))).convert('RGBA'))
 generated=[]
 out=ROOT/'exports/Tiangong-Xianzhen-Art-v160.7.zip'
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  z.writestr('mod.json',json.dumps(meta,ensure_ascii=False,indent=2))
  z.writestr('bundles/bundle.properties','app.name=天工仙阵\n')
  z.writestr('bundles/bundle_zh_CN.properties','app.name=天工仙阵\n')
  for r in rows:
   assert sha(ROOT/r['file'])==r['sha256'],r['file']
   target=r['target'];name=Path(target).stem
   if '-autotile'in name:
    source=np.array(Image.open(ROOT/r['file']).convert('RGBA'));size=source.shape[0];cell=size//4;assert source.shape[1]==size and size%4==0
    positions={tuple(layout[y*32,x*32]):(x*cell,y*cell)for x in range(4)for y in range(4)}
    base=name.replace('-autotile','-'if name[-1].isdigit()else'')
    for i in range(47):
     tile=np.zeros((cell,cell,4),dtype='uint8');cx=i%12;cy=i//12
     for y in range(cell):
      for x in range(cell):
       point=positions.get(tuple(layout[(cy*cell+y)*128//size,(cx*cell+x)*384//(size*3)]))
       if point is not None:tile[y,x]=source[point[1]+y,point[0]+x]
     data=io.BytesIO();Image.fromarray(tile).save(data,format='PNG');name_=str(Path(target).parent/(base+'-'+str(i)+'.png')).replace('\\','/');z.writestr(name_,data.getvalue());generated.append({'source':r['file'],'target':name_,'sha256':hashlib.sha256(data.getvalue()).hexdigest()})
   elif target=='sprites-override/ui/logo.png':
    im=Image.open(ROOT/'branding/tiangong-xianzhen/tiangong-xianzhen-logo.png');im.thumbnail((640,320),Image.Resampling.LANCZOS);data=io.BytesIO();im.save(data,format='PNG');z.writestr(target,data.getvalue())
   else:z.write(ROOT/r['file'],target)
  for p in classes.rglob('*.class'):z.write(p,p.relative_to(classes).as_posix())
  for name in ['ATTRIBUTION.md']:z.write(ROOT/name,name)
  z.write(ROOT/'records/reference-ui-sources/LICENSE-Mindustry-v160.7','LICENSE-Mindustry-v160.7')
  z.write(HERE/'src/tiangong/BrandMod.java','source/BrandMod.java')
  z.write(generator,'source/ImageTileGenerator.java')
  z.writestr('ART-MANIFEST.json',json.dumps({'sourceCommit':c['sourceCommit'],'count':len(rows),'assets':rows},indent=2))
 report={'builtAt':datetime.now(timezone.utc).isoformat(),'file':out.relative_to(ROOT).as_posix(),'sha256':sha(out),'bytes':out.stat().st_size,'resources':len(rows),'runtimeAutotileRegions':len(generated),'runtimeVerified':False,'supportedLoadingRoute':'Mods.packSprites sprites-override, new explicit regions, post-initialization original createIcons pipeline and FileTree replacement; original content ownership and gameplay fields unchanged','assets':rows,'generatedAutotileRegions':generated,'autotileCodeEvidence':{'file':'full-game/integration/upstream/ImageTileGenerator.java','sha256':sha(generator),'source':'https://github.com/Anuken/Mindustry/blob/17012d61d9e4c3cbd9820d87e81c24495486ac53/tools/src/mindustry/tools/ImageTileGenerator.java'}}
 (HERE/'mod-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 game=work/'game-data';(game/'mods').mkdir(parents=True,exist_ok=True);shutil.copyfile(out,game/'mods/tiangong-xianzhen-art.zip')
 print(json.dumps({k:v for k,v in report.items()if k not in ['assets','generatedAutotileRegions']}))
if __name__=='__main__':main()
