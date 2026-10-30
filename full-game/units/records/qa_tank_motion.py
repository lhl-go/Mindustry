from build import *

m=rd(B/'manifest.json');a={x['id']:x for x in m['assets']};f={x['id']:x for x in m['generatedAtlasRegions']}
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14);checks=[];views=[]
def render(unit,frame):
 body=Image.open(R/a[unit]['file']).convert('RGBA');tr=a[unit+'-treads'];t=Image.open(R/tr['file']).convert('RGBA');size=(max(body.width,t.width),max(body.height,t.height));c=Image.new('RGBA',size);off=[round((size[0]-t.width)/2),round((size[1]-t.height)/2)];c.alpha_composite(t,tuple(off))
 for i,pl in enumerate(tr['registration']['placements']):
  strip=Image.open(R/f[f'{unit}-treads{i}-{frame}']['file']).convert('RGBA')
  for side in ['left','right']:
   x,y,w,h=pl[side];c.alpha_composite(strip.resize((w,h),Image.Resampling.NEAREST),(x+off[0],y+off[1]))
 c.alpha_composite(body,(round((size[0]-body.width)/2),round((size[1]-body.height)/2)))
 return c
for unit in ['stell','locus','precept','vanquish','conquer']:
 c0=render(unit,0);c9=render(unit,9);arr0=np.array(c0);arr9=np.array(c9);changed=np.any(arr0!=arr9,axis=2);tr=a[unit+'-treads'];body=Image.open(R/a[unit]['file']).convert('RGBA');canvas=Image.new('RGBA',tuple(tr['size']));canvas.alpha_composite(body,(round((canvas.width-body.width)/2),round((canvas.height-body.height)/2)));ba=np.array(canvas)[:,:,3];exposure=[]
 for i,pl in enumerate(tr['registration']['placements']):
  for side in ['left','right']:
   x,y,w,h=pl[side];part=ba[max(0,y):min(canvas.height,y+h),max(0,x):min(canvas.width,x+w)];exposure.append(dict(group=i,side=side,uncoveredFraction=round(float((part<128).mean()),4)))
 assert min(x['uncoveredFraction'] for x in exposure)>.5,(unit,exposure)
 assert changed.sum()>20,(unit,'no visible movement')
 diff=Image.new('RGBA',c0.size);ar=np.array(diff);ar[changed]=[120,240,170,255];diff=Image.fromarray(ar)
 checks.append(dict(id=unit,bodyFile=a[unit]['file'],bodySha256=a[unit]['sha256'],treadFile=tr['file'],treadSha256=tr['sha256'],treadBeforeBody=True,frameComparison=[0,9],visibleChangedPixels=int(changed.sum()),exposedMotionRectangles=exposure,status='passed_static_draw_order_and_frame_visibility',engineNotVerified=True))
 views.append((unit,c0,c9,diff))
for label,bg in [('dark',(28,39,38)),('light',(245,240,222))]:
 sheet=Image.new('RGB',(1000,len(views)*310),bg);d=ImageDraw.Draw(sheet)
 for n,(unit,*ims) in enumerate(views):
  for col,im in enumerate(ims):
   s=min(290/im.width,265/im.height);im=im.resize((round(im.width*s),round(im.height*s)),Image.Resampling.NEAREST);tile=Image.new('RGBA',(320,270),(*bg,255));tile.alpha_composite(im,((320-im.width)//2,(270-im.height)//2));sheet.paste(tile.convert('RGB'),(col*330,n*310));d.text((col*330+10,n*310+280),unit+' / '+['frame 0','frame 9','visible difference'][col],font=font,fill=(220,225,210) if label=='dark' else (30,45,35))
 p=B/'qa'/f'tank-motion-{label}.png';sheet.save(p);wr(Path(str(p)+'.generation.json'),dict(file=rel(p),sha256=sha(p),operation='QA simulation only: source-defined tread/frame placement first, body overlay second, enlarged pixels for review; final column visualizes actual changed pixels',derivedFrom=[srcinfo(R/a[u]['file']) for u in ['stell','locus','precept','vanquish','conquer']]+[srcinfo(R/x['file']) for x in m['generatedAtlasRegions']]))
wr(B/'qa/tank-motion.json',dict(status='passed_numeric_pending_visual',sourceCode=dict(file='records/reference-unit-sources/UnitType.java',sha256=sha(R/'records/reference-unit-sources/UnitType.java'),drawOrderLines=[1513,1546],drawTankLines=[1806,1824]),checks=checks,engineNotVerified=True));print(json.dumps(checks))
