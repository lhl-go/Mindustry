from build import *
from PIL import ImageFilter
import math
def rel(p):return p.relative_to(ROOT).as_posix()
def excerpt_record(p,a,b):
 lines=p.read_text(encoding='utf-8').splitlines();return dict(file=rel(p),sha256=sha(p),lineStart=a,lineEnd=b,exactSource='\n'.join(lines[a-1:b]))
def fx():
 p=BASE/'references/Fx.java';s=p.read_text(encoding='utf-8');matches=list(re.finditer(r'^    (\w+)\s*=\s*new Effect\(',s,re.M));out=[]
 for i,m in enumerate(matches):
  end=matches[i+1].start() if i+1<len(matches) else s.rfind('\n}')
  body=s[m.start():end].rstrip();first=body.split('new Effect(',1)[1].split(',',1)[0].strip();simple=first.replace('f','');numeric=eval(simple,{'__builtins__':{}},{}) if re.fullmatch(r'[0-9.\s*+()/\-]+',simple) else None
  atlas=sorted(set(re.findall(r'Core\.atlas\.find\("([^"]+)"\)',body)));icons=sorted(set(re.findall(r'Icon\.(\w+)\.getRegion',body)))
  dyn=[]
  for token in ['unit.fullIcon','block.fullIcon','type.fullIcon','uiIcon','TextureRegion','Trail','Fire.regions','data.region','Leg','BuildPayload']:
   if token in body:dyn.append(token)
  # Full source remains the authority for callback parameters and conditional branches.
  out.append(dict(id='Fx.'+m[1],name=m[1],implementation='retain_official_runtime_callback',requiresNewRaster=False,lifetimeTicksExpression=first,lifetimeTicksConstant=numeric,lifetimeIsRuntimeMutable='e.lifetime =' in body or 'b.lifetime =' in body,atlasRegionDependencies=atlas,iconDependencies=icons,dynamicSpriteInputs=dyn,source=dict(file=rel(p),sha256=sha(p),lineStart=s[:m.start()].count('\n')+1,lineEnd=s[:end].count('\n')),exactImplementation=body,implementationSha256=hashlib.sha256(body.encode()).hexdigest(),geometryPolicy='Keep Fill/Lines/Drawf geometry, palette and easing from pinned source. New art is used through the mapped atlas names and dynamic content icons.',newStaticSpriteIsNotAReplacement=True))
 write(BASE/'runtime-fx.json',dict(commit='17012d61d9e4c3cbd9820d87e81c24495486ac53',count=len(out),effects=out,source=rel(p),sourceSha256=sha(p),runtimeVerification=False))
 return len(out)
def content():
 out={}
 for filename,typ in [('Items.java','Item'),('Liquids.java',r'(?:Liquid|CellLiquid)'),('StatusEffects.java','StatusEffect')]:
  p=BASE/'references'/filename;s=p.read_text(encoding='utf-8');rows=[];mm=list(re.finditer(r'(\w+)\s*=\s*new '+typ+r'\("([^"]+)"',s))
  for i,m in enumerate(mm):
   body=s[m.start():mm[i+1].start() if i+1<len(mm) else len(s)];name=m[2];prefix='item-' if filename=='Items.java' else 'liquid-' if filename=='Liquids.java' else 'status-';id=prefix+name
   rows.append(dict(javaField=m[1],name=name,atlasRegion=id if (BASE/'assets'/f'{id}.png').exists() else None,assetFile=rel(BASE/'assets'/f'{id}.png') if (BASE/'assets'/f'{id}.png').exists() else None,noRasterReason=None if (BASE/'assets'/f'{id}.png').exists() else 'No independent source-tree raster; none is an empty status, invincible/dynamic are hidden runtime status definitions.',showStatusIconFalse='show = false' in body,gas='gas = true' in body,sourceLine=s[:m.start()].count('\n')+1,sourceFile=rel(p),sourceSha256=sha(p)))
  out[filename]=rows
 write(BASE/'runtime-content.json',dict(commit='17012d61d9e4c3cbd9820d87e81c24495486ac53',content=out,rendering='Items/liquids/status icons map by exact atlas name. All numeric gameplay behavior remains in fixed official source.'))
 return {k:len(v) for k,v in out.items()}
def technical_generated():
 p=BASE/'references/Generators.java';source=excerpt_record(p,109,190);rows=[]
 for kind,n,size in [('splash',12,32),('bubble',16,40)]:
  for i in range(n):
   fin=np.float32(i)/np.float32(n);fout=np.float32(1)-fin;stroke=np.float32(3.5)*fout;radius=np.float32(size/2)*fin;yy,xx=np.mgrid[:size,:size];dst=np.sqrt((xx-np.float32(size/2)).astype('float32')**2+(yy-np.float32(size/2)).astype('float32')**2).astype('float32');mask=np.abs(dst-radius)<=stroke
   if kind=='bubble':
    shinelen=radius/np.float32(2.5);shinerad=stroke*np.float32(1.5)+np.float32(.3);shinex=np.float32(size/2)+shinelen/np.float32(math.sqrt(2));shiney=np.float32(size/2)-shinelen/np.float32(math.sqrt(2));mask|=((xx-shinex).astype('float32')**2+(yy-shiney).astype('float32')**2)<shinerad**2
   a=np.zeros((size,size,4),dtype='uint8');a[mask]=255;im=Image.fromarray(a);dstp=BASE/'engine/generated'/f'{kind}-{i}.png';dstp.parent.mkdir(parents=True,exist_ok=True);im.save(dstp)
   rec=dict(file=rel(dstp),sha256=sha(dstp),width=size,height=size,format='PNG',mode='RGBA',artSource='official_procedural_mask_algorithm',operation=dict(type='deterministic_reproduction_of_pinned_Generators',frame=i,frames=n,size=size,fin=float(fin),stroke=float(stroke),radius=float(radius),numericPrecision='float32 geometry; integer texel coordinates',alpha='binary 0/255',authoring='No novel pictorial art drawn. Exact technical ring-mask formula retained.'),source=excerpt_record(p,109 if kind=='splash' else 136,134 if kind=='splash' else 161),actualModel=None,actualQuality=None,unverifiedReason='Not model generated; runtime technical mask formula.',engineNotVerified=True)
   write(dstp.with_name(dstp.name+'.generation.json'),rec);rows.append(dict(id=f'{kind}-{i}',file=rel(dstp),sha256=sha(dstp),generationRecord=rel(dstp)+'.generation.json',size=[size,size],sourceGenerated=True,status='official_formula_exported'))
 # The fluid stencil is an engine technical mask, retained byte-for-byte with its source identity.
 stencilSource=ROOT/'full-game/blocks/reference-sprites/blocks/liquid/fluid.png';stencil=BASE/'runtime-inputs/fluid.png';stencil.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(stencilSource,stencil);bb=stencil.read_bytes();blob=hashlib.sha1(('blob '+str(len(bb))+'\0').encode()+bb).hexdigest();assert blob=='d2896d5c7b50ecb9800a73d57937a56deda90d05'
 write(stencil.with_name(stencil.name+'.generation.json'),dict(file=rel(stencil),sha256=sha(stencil),mode=Image.open(stencil).mode,width=Image.open(stencil).width,height=Image.open(stencil).height,format='PNG',artSource='exact_official_technical_stencil',officialSource=dict(repository='Anuken/Mindustry',commit='17012d61d9e4c3cbd9820d87e81c24495486ac53',path='core/assets-raw/sprites/blocks/liquid/fluid.png',gitBlobSha1=blob),operation='byte-identical runtime atlas build input; required by Generators gas-frames',actualModel=None,actualQuality=None,unverifiedReason='Not AI art; official mask.'))
 fluid=[]
 for kind,scale,phase in [('liquid',230,3),('gas',190,4)]:
  for i in range(50):fluid.append(dict(id=f'fluid-{kind}-{i}',implementation='retain_official_build_time_generator',status='covered_by_pinned_generator_and_retained_stencil',requiresNewArt=False,generator='Generators.run generate("gas-frames")',stencilFile=rel(stencil),stencilSha256=sha(stencil),sourceFile=rel(p),sourceSha256=sha(p),sourceLines=[163,190],pixelFormulaFunctionsSourceLines=[32,67],frame=i,frameCount=50,frameParameter=f'{i}/50f',baseRgb='white',alphaFormula='fluid('+('true' if kind=='gas' else 'false')+',x,y,frame)',alphaWriteGate='base.getA(x,y)>128',uvSize=list(Image.open(stencil).size),runtimeFrameFormula=f'int(Time.time/{scale}f*50+liquid.id*5)%50',loopDurationTicks=scale,drawTint='Liquid.color',outputIncluded=False,outputReason='Technical atlas mask generated by the official asset build from the included exact algorithm and stencil, not a separately hand-authored PNG.'))
 write(BASE/'runtime-atlas.json',dict(commit='17012d61d9e4c3cbd9820d87e81c24495486ac53',generatedRegionCount=128,exportedTechnicalMaskCount=28,retainedBuildTimeGeneratedCount=100,exported=rows,fluidRegions=fluid,exactGeneratorSource=excerpt_record(p,32,190),runtimeSource=excerpt_record(BASE/'references/Liquid.java',102,109),closedInputs=[dict(file=rel(stencil),sha256=sha(stencil),generationRecord=rel(stencil)+'.generation.json')],integration='Run the pinned Mindustry sprite packer gas-frames generator as part of the unchanged official asset build; it creates all 100 fluid names before Renderer.loadFluidFrames. Included source and stencil close the dependency; no external art is missing.',engineNotVerified=True))
 return rows
if __name__=='__main__':
 print(json.dumps(dict(fx=fx(),content=content(),technicalMasks=len(technical_generated()))))
