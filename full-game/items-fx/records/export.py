from build import *
def export():
 assets=[]
 for rp in sorted((BASE/'records').glob('*.receipt.json')):
  j=json.loads(rp.read_text(encoding='utf-8'));stem=j['stem'];src=BASE/'source'/f'{stem}.png'
  if not src.exists():continue
  im=Image.open(src).convert('RGBA');cols=j.get('cols',4);rows=j.get('rows',2)
  if len(j['names'])==6 and 'cols' not in j:cols=3
  for i,name in enumerate(j['names']):
   custom={'09-rubble-small':[[0,0,490,455],[490,0,965,455],[965,0,1536,475],[0,475,550,1024],[550,475,1536,1024]],'10-rubble-large':[[0,0,430,480],[430,0,980,480],[980,0,1536,480],[0,480,730,1024],[730,480,1536,1024]]}
   box=custom[stem][i] if stem in custom else [round((i%cols)*im.width/cols),round((i//cols)*im.height/rows),round((i%cols+1)*im.width/cols),round((i//cols+1)*im.height/rows)];arr=np.array(im.crop(box));a=arr[:,:,3];a[a<16]=0;a[a>=245]=255;arr[a==0,:3]=0
   cut=Image.fromarray(arr);b=cut.getbbox()
   if not b:continue
   cut=cut.crop(b);out=Image.new('RGBA',(cut.width+32,cut.height+32));out.alpha_composite(cut,(16,16));dst=BASE/'assets'/f'{name}.png';out.save(dst)
   rec=dict(file=dst.relative_to(ROOT).as_posix(),sha256=sha(dst),width=out.width,height=out.height,format='PNG',mode='RGBA',derivedFrom=[dict(file=src.relative_to(ROOT).as_posix(),sha256=sha(src),generationRecord=src.relative_to(ROOT).as_posix()+'.generation.json')],operation=dict(type='native_cell_crop_alpha_cleanup',crop=box,trim=list(b),padding=16,alphaBelow16ToZero=True,alphaAtLeast245To255=True,transparentRgbZeroed=True),upsampled=False,actualModel=None,actualQuality=None,unverifiedReason='See source generation record; host actual model and quality undisclosed.')
   write(dst.with_name(dst.name+'.generation.json'),rec);assets.append(dict(id=name,file=rec['file'],sha256=rec['sha256'],size=[out.width,out.height],generationRecord=rec['file']+'.generation.json',anchorNormalized=[.5,.5],status='exported_pending_visual_qa'))
 write(BASE/'manifest.json',dict(status='in_production',assets=assets,assetCount=len(assets)))
 cols=8;tw=180;th=215;sheet=Image.new('RGB',(cols*tw,((len(assets)+cols-1)//cols)*th),(232,226,209));d=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12)
 for i,a in enumerate(assets):
  s=Image.open(ROOT/a['file']).convert('RGBA');s.thumbnail((170,170));tile=Image.new('RGBA',(170,170),(30,42,40,255) if i%2 else (245,240,222,255));tile.alpha_composite(s,((170-s.width)//2,(170-s.height)//2));x=i%cols*tw;y=i//cols*th;sheet.paste(tile.convert('RGB'),(x+5,y+5));d.text((x+5,y+180),a['id'],font=font,fill=(20,60,45))
 sheet.save(BASE/'contact.png');write(BASE/'contact.png.generation.json',dict(file=(BASE/'contact.png').relative_to(ROOT).as_posix(),sha256=sha(BASE/'contact.png'),operation='Downsampled QA contact, actual alpha composite',derivedFrom=[dict(file=a['file'],sha256=a['sha256'],generationRecord=a['generationRecord']) for a in assets]));print(json.dumps({'exported':len(assets)}))
if __name__=='__main__':export()
