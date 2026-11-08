"""Static art, geometry and layer-order QA; this does not launch the engine."""
from export_common import *
from collections import Counter
import math

BATCH=HERE/'batches/hud_review.json'
m=read(BATCH);rows=m['sourceMappings'];by={a['region']:a for a in rows}
errors=[];checks=[]
for a in rows:
 p=ROOT/a['file'];im=Image.open(p).convert('RGBA');arr=np.asarray(im)
 op,orig=original(ROWS[a['region']]);oa=np.asarray(orig);issues=[]
 if sha(p)!=a['sha256']:issues.append('output_hash')
 if sha(ROOT/a['nativeFile'])!=a['nativeSha256']:issues.append('native_hash')
 if im.size!=orig.size:issues.append('source_canvas')
 if orig.getchannel('A').getbbox() and not im.getchannel('A').getbbox():issues.append('unexpected_empty')
 if a['disposition']=='exact_upstream_technical_reuse' and sha(p)!=sha(op):issues.append('technical_bytes')
 if a['operation'].get('exactOriginalAlpha') and not np.array_equal(arr[:,:,3],oa[:,:,3]):issues.append('functional_alpha')
 if a['disposition']=='retained_functional_effect_geometry':
  if not np.array_equal(arr[:,:,3],oa[:,:,3]):issues.append('directional_effect_alpha')
  if np.any(arr[:,:,:3][arr[:,:,3]>0]!=255):issues.append('nonneutral_tint')
 checks.append({'region':a['region'],'file':a['file'],'sha256':sha(p),'issues':issues})
 errors.extend(a['region']+':'+x for x in issues)
expected={a['sourcePath'] for a in ROWS.values() if a['category'] in ['production','power','drills']}
actual={a['sourcePath'] for a in rows}
if actual!=expected or len(actual)!=len(rows):errors.append('source_path_coverage')
for a in m['integrationGeometryInputs']:
 if sha(ROOT/a['file'])!=a['sha256']:errors.append('input_hash:'+a['file'])

def get(name):return Image.open(ROOT/by[name]['file']).convert('RGBA')
SIZE=256;SCALE=2
def place(out,im,angle=0,dx=0,dy=0):
 im=im.resize((im.width*SCALE,im.height*SCALE),Image.Resampling.NEAREST)
 if angle:im=im.rotate(angle,Image.Resampling.BICUBIC,expand=True)
 out.alpha_composite(im,(round((SIZE-im.width)/2+dx*SCALE),round((SIZE-im.height)/2-dy*SCALE)))
def base(bg=(25,45,47)):return Image.new('RGBA',(SIZE,SIZE),(*bg,255))
def tint(im,color,alpha=1):
 a=np.asarray(im).copy();a[:,:,:3]=color;a[:,:,3]=(a[:,:,3]*alpha).astype('uint8');return Image.fromarray(a)
def additive(out,im,angle=0,alpha=1,color=(255,170,60)):
 layer=Image.new('RGBA',(SIZE,SIZE));place(layer,tint(im,color,alpha),angle)
 a=np.asarray(out).copy();b=np.asarray(layer).astype(float);a[:,:,:3]=np.clip(a[:,:,:3].astype(float)+b[:,:,:3]*b[:,:,3,None]/255,0,255).astype('uint8');return Image.fromarray(a)
frames=[];motion=[]
def save_pair(name,fn,description):
 pair=[fn(phase)for phase in [0,1]]
 diff=int(np.count_nonzero(np.any(np.asarray(pair[0])[:,:,:3]!=np.asarray(pair[1])[:,:,:3],axis=2)))
 if diff==0:errors.append('invisible_motion:'+name)
 frames.extend((name+' / '+label,p)for label,p in zip(['phase A','phase B'],pair))
 motion.append({'id':name,'changedPixelsAt2x':diff,'layerOrder':description,'engineExecuted':False})

for bid in ['mechanical-drill','pneumatic-drill','laser-drill','blast-drill','water-extractor','oil-extractor','pulverizer']:
 def rotor_frame(phase,bid=bid):
  o=base();place(o,get(bid));place(o,get(bid+'-rotator'),phase*37);place(o,get(bid+'-top'));return o
 save_pair(bid,rotor_frame,'base, independent rotating rotor, small stationary hub cap')
 rotor=get(bid+'-rotator');cap=get(bid+'-top');alpha=Image.new('RGBA',rotor.size);alpha.alpha_composite(cap,((rotor.width-cap.width)//2,(rotor.height-cap.height)//2))
 ra=np.asarray(rotor)[:,:,3]/255;ca=np.asarray(alpha)[:,:,3]/255
 visible=float((ra*(1-ca)).sum()/max(ra.sum(),1));motion[-1]['rotorAlphaVisibleAfterHub']=visible
 if visible<.10:errors.append('hub_hides_rotor:'+bid)

for bid,suffix in [('separator','-spinner'),('disassembler','-spinner'),('vent-condenser','-rotator')]:
 def window_rotor(phase,bid=bid,suffix=suffix):
  o=base();place(o,get(bid+'-bottom'));place(o,get(bid+suffix),phase*37)
  if bid+'-mid' in by:place(o,get(bid+'-mid'))
  place(o,get(bid));return o
 save_pair(bid,window_rotor,'bottom, independent rotor, optional center, original-window body')

def turbine(phase):
 o=base();place(o,get('turbine-condenser'));place(o,get('turbine-condenser-rotator'),phase*37);return o
save_pair('turbine-condenser',turbine,'body then independent rotor')
def steam(phase):
 o=base();place(o,get('steam-generator'))
 place(o,get('steam-generator-turbine'),phase*37)
 place(o,get('steam-generator-turbine'),45-phase*37)
 place(o,get('steam-generator-cap'))
 place(o,tint(get('steam-generator-liquid'),(80,150,230),.6));return o
save_pair('steam-generator',steam,'body, two counter-rotating turbine instances, static hub, tinted liquid stencil')
for bid in ['phase-weaver','phase-synthesizer']:
 def weave(phase,bid=bid):
  o=base();place(o,get(bid+'-bottom'));place(o,get(bid+'-weave'),phase*51)
  if bid=='phase-synthesizer':place(o,get(bid+'-weave'),phase*-45.9)
  place(o,get(bid));return o
 save_pair(bid,weave,'bottom, one or two counter-rotating weave layers, window body')

for bid,sides,mag in [('spore-press',4,4),('chemical-combustion-chamber',4,3),('pyrolysis-generator',8,3)]:
 def pistons(phase,bid=bid,sides=sides,mag=mag):
  o=base();place(o,get(bid+'-bottom'));length=(-1+phase*mag)*4
  for i in range(sides):
   angle=i*360/sides;rn=bid+'-piston'+('1'if 135<=angle<315 else'0')
   if rn not in by:rn=bid+'-piston'
   if bid+'-piston-t'in by and angle in[135,315]:rn=bid+'-piston-t'
   part=get(rn)
   if angle==315:part=ImageOps.flip(part)
   place(o,part,angle,math.cos(math.radians(angle))*length,math.sin(math.radians(angle))*length)
  if bid+'-mid'in by:place(o,get(bid+'-mid'))
  place(o,get(bid));return o
 save_pair(bid,pistons,'bottom, 4/8 independent radially translated pistons, optional center, window body; fixture uses motion endpoints')

def plasma(phase):
 o=base();place(o,get('impact-reactor-bottom'))
 for i in range(4):o=additive(o,get('impact-reactor-plasma-'+str(i)),phase*(12+i*6),.5,color=(255,208-38*i,107-24*i))
 place(o,get('impact-reactor'));return o
save_pair('impact-reactor',plasma,'bottom, all four additive plasma layers simultaneously, window body; phase alters each rotation')
for bid in ['electric-heater','heat-redirector','heat-router','phase-heater']:
 def heat(phase,bid=bid):
  o=base();place(o,get(bid));place(o,get(bid+('-top1' if phase==0 else'-top2')),phase*180)
  o=additive(o,get(bid+'-heat'),phase*180,.7,(255,56,56));return o
 save_pair(bid,heat,'fixed body, direction-selected top1/top2, separately rotated single-edge red heat mask')
def diode(phase):
 o=base();place(o,get('diode'));place(o,get('diode-arrow'),phase*90);return o
save_pair('diode',diode,'fixed jade plate with baked arrow removed, independent direction arrow at 0/90 degrees')

contacts=[]
for start in range(0,len(frames),12):
 group=frames[start:start+12];page=Image.new('RGB',(4*280,3*300),(230,228,214));d=ImageDraw.Draw(page)
 for i,(label,im)in enumerate(group):
  x=i%4*280;y=i//4*300;page.paste(im.convert('RGB'),(x+12,y+10));d.text((x+6,y+270),label,fill=(20,40,36))
 p=HERE/'qa'/f'industry-assembly-{start//12+1:02}.png';page.save(p);contacts.append({'file':rel(p),'sha256':sha(p)})
report={'checkedAt':datetime.now(timezone.utc).isoformat(),'sourceCount':len(rows),'expectedCount':251,
 'errors':errors,'checks':checks,'motionChecks':motion,'assemblyContacts':contacts,
 'dispositions':dict(Counter(a['disposition']for a in rows)),
 'scope':'Static source canvases, hashes, neutral masks, original functional geometry and source-informed layer-order compositions. Fixtures omit procedural particles, full liquid animation and actual engine lighting.','runtimeIntegrationVerified':False}
write(HERE/'qa/industry-validation.json',report)
print(json.dumps({k:v for k,v in report.items()if k not in ['checks','motionChecks']}));print(json.dumps(motion))
if errors:raise SystemExit(1)
