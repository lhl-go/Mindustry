"""Static layer-order inspection aids, not engine screenshots or new art."""
from export_common import *
import re
B=read(HERE/'batches/root.json');M={a['region']:a for a in B['sourceMappings']};used=set();cards=[];checks=[]
def im(n):
 used.add(n);return Image.open(ROOT/M[n]['file']).convert('RGBA')
def center(dst,src):dst.alpha_composite(src,((dst.width-src.width)//2,(dst.height-src.height)//2))
for family in ['conduit','pulse-conduit','plated-conduit','reinforced-conduit']:
 for state in [0,1,2,3,4]:
  top=im(f'{family}-top-{state}');bot=im(f'conduit-bottom-{state}');a=np.asarray(bot).copy();a[:,:,:3]=[57,150,224];liquid=Image.fromarray(a)
  out=Image.new('RGBA',top.size);center(out,liquid);center(out,top);cards.append((f'{family} / join {state}',out))
for name in ['liquid-router','liquid-container','liquid-tank','reinforced-liquid-router','reinforced-liquid-container','reinforced-liquid-tank']:
 top=im(name);_,orig=original(ROWS[name]);bot=im(name+'-bottom');out=Image.new('RGBA',top.size);center(out,bot)
 # Match the renderer's rectangular world-space padding (four source pixels per world unit).
 definition=DEFS[name]['definition'];m=re.search(r'liquidPadding\s*=\s*([\d.f/]+)',definition);terms=(m.group(1)if m else'0').replace('f','').split('/');padding=float(terms[0])/(float(terms[1])if len(terms)>1 else 1);pad=round(padding*4)
 a=np.asarray(orig)[:,:,3];fill=np.zeros((*a.shape,4),dtype='uint8');fill[:,:,:3]=[57,150,224];fill[pad:top.height-pad if pad else top.height,pad:top.width-pad if pad else top.width,3]=255
 out.alpha_composite(Image.fromarray(fill));center(out,top);cards.append((name+' / window visibility',out))
 checks.append({'region':name,'originalFrameAlphaUnchanged':bool(np.array_equal(np.asarray(top)[:,:,3],a))})
for name in ['door','door-large','blast-door']:
 for suffix in ['', '-open']:cards.append((name+suffix,im(name+suffix)))
for name in ['core-shard','core-foundation','core-nucleus','core-bastion','core-citadel','core-acropolis']:
 body=im(name);part=im(name+'-thruster1');out=Image.new('RGBA',(max(body.width,part.width,part.height)+40,)*2)
 for i in range(4):center(out,im(name+('-thruster1'if i<2 else'-thruster2')).rotate(i*90,expand=True))
 center(out,body);cards.append((name+' / body over 4 thrusters',out))
for deg in [0,90,180,270]:
 base=im('mass-driver-base');head=im('mass-driver').rotate(deg,expand=True);out=Image.new('RGBA',(max(base.width,head.width)+12,max(base.height,head.height)+12));center(out,base);center(out,head);cards.append(('mass-driver / head '+str(deg),out))
paths=[]
for start in range(0,len(cards),24):
 group=cards[start:start+24];out=Image.new('RGB',(1440,((len(group)+5)//6)*240),(233,226,208));d=ImageDraw.Draw(out)
 for k,(label,pic)in enumerate(group):
  x=k%6*240;y=k//6*240;d.rectangle((x,y,x+237,y+209),fill=(25,45,47));pic=ImageOps.contain(pic,(216,190),Image.Resampling.NEAREST);out.paste(pic,(x+(240-pic.width)//2,y+(204-pic.height)//2),pic);d.text((x+4,y+213),label[:38],fill=(25,45,47))
 p=HERE/'qa'/f'root-assembly-{start//24+1:02}.png';out.save(p);paths.append(rel(p))
write(HERE/'qa/root-assembly.json',{'checkedAt':datetime.now(timezone.utc).isoformat(),'purpose':'Static alpha/layer-order inspection only; not an engine run. Liquid fill is a solid inspection color and core thrusters use their extended canvas anchors.','checks':checks,'images':[{'file':p,'sha256':sha(ROOT/p)}for p in paths],'inputs':[{'file':M[n]['file'],'sha256':M[n]['sha256']}for n in sorted(used)],'runtimeIntegrationVerified':False})
print(json.dumps({'images':paths,'checks':checks}))
