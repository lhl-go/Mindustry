from build import *
def make_contact(items,path,bg,maskMode=False):
 cols=5;cw=245;ch=218;sheet=Image.new('RGB',(cols*cw,math.ceil(len(items)/cols)*ch),bg);d=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',11)
 for i,a in enumerate(items):
  im=Image.open(R/a['file']).convert('RGBA');isMask=a['role'].endswith('_mask')
  if maskMode and isMask:
   base=Image.open(R/a['maskBaseFile']).convert('RGBA');canvas=Image.new('RGBA',im.size);canvas.alpha_composite(base,tuple(a['maskRegistrationOffset']));color=Image.new('RGBA',im.size,(255,70,20,0) if a['role']=='heat_mask' else (70,225,255,0));color.putalpha(im.getchannel('A'));canvas.alpha_composite(color);im=canvas
  # Contact-only nearest-neighbor enlargement exposes low-resolution atlas texels; engine file is unchanged.
  s=min(212/im.width,175/im.height);im=im.resize((max(1,round(im.width*s)),max(1,round(im.height*s))),Image.Resampling.NEAREST if s>1 else Image.Resampling.LANCZOS);tile=Image.new('RGBA',(225,180),(*bg,255));tile.alpha_composite(im,((225-im.width)//2,(180-im.height)//2));x=i%cols*cw;y=i//cols*ch;sheet.paste(tile.convert('RGB'),(x+10,y+4));d.text((x+8,y+188),a['id']+' '+str(a['size']),font=font,fill=(225,225,210) if sum(bg)<300 else (30,50,42));d.text((x+8,y+202),a['role'],font=font,fill=(170,170,150) if sum(bg)<300 else (90,95,80))
 sheet.save(path);wr(Path(str(path)+'.generation.json'),dict(file=rel(path),sha256=sha(path),operation='QA contact only; nearest-neighbor magnification for engine texel inspection, not native art',derivedFrom=[srcinfo(R/a['file']) for a in items]))
def main():
 m=rd(B/'manifest.json');q=B/'qa';q.mkdir(exist_ok=True);issues=[];checks=[]
 for a in m['assets']:
  im=Image.open(R/a['file']).convert('RGBA');al=np.array(im)[:,:,3];err=[];leaks=None
  if sha(R/a['file'])!=a['sha256']:err.append('hash')
  if list(im.size)!=a['sourceDimensions']:err.append('dimensions')
  if not al.any():err.append('empty')
  if a['role'].endswith('_mask'):
   base=Image.open(R/a['maskBaseFile']).convert('RGBA');tmp=Image.new('RGBA',im.size);tmp.alpha_composite(base,tuple(a['maskRegistrationOffset']));ba=np.array(tmp)[:,:,3];leaks=int(((al>0)&(ba==0)).sum())
   if leaks:err.append('mask_outside_new_body')
  checks.append(dict(id=a['id'],file=a['file'],sha256=a['sha256'],size=a['size'],maskLeakPixels=leaks,issues=err));issues.extend(a['id']+':'+x for x in err)
 art=[a for a in m['assets'] if not a['role'].endswith('_mask')];masks=[a for a in m['assets'] if a['role'].endswith('_mask')];contacts=[]
 for kind,arr in [('atlas',art),('masks',masks)]:
  for n in range(0,len(arr),45):
   for label,bg in [('dark',(28,39,38)),('light',(245,240,222))]:
    p=q/f'{kind}-{n//45+1:02}-{label}.png';make_contact(arr[n:n+45],p,bg,kind=='masks');contacts.append(rel(p))
 wr(q/'report.json',dict(status='numeric_pass_pending_visual' if not issues else 'issues_found',sourceCount=290,checkedCount=len(checks),uniqueSourcePaths=len({a['sourcePath'] for a in m['assets']}),issues=issues,checks=checks,contacts=contacts,maskCount=len(masks),allMaskPixelsInsideNewShape=all(c['maskLeakPixels'] in [0,None] for c in checks),extraAtlasRegions=m['additionalAtlasRegions'],engineNotVerified=True));m['qaReport']=rel(q/'report.json');m['contacts']=contacts;wr(B/'manifest.json',m);print(json.dumps({'issues':issues,'contacts':contacts}))
if __name__=='__main__':main()
