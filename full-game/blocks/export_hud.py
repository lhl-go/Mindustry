"""Production/power/drill export; exact source canvases and runtime layer roles.

Local pixel work is a documented derivation from accepted painted art, not AI
generation. The original geometry inputs are retained for reproducibility.
"""
from export_common import *
from PIL import ImageFilter
import re

CATEGORIES=['production','power','drills']
OWN=[a for a in ROWS.values() if a['category'] in CATEGORIES]
geometry=[]
cache={}
CAPS={'mechanical-drill','pneumatic-drill','laser-drill','blast-drill',
      'water-extractor','oil-extractor'}
ROTORS={'mechanical-drill-rotator','pneumatic-drill-rotator','laser-drill-rotator',
 'blast-drill-rotator','water-extractor-rotator','oil-extractor-rotator',
 'cliff-crusher-rotator','large-cliff-crusher-rotator','separator-spinner',
 'disassembler-spinner','pulverizer-rotator','steam-generator-turbine',
 'turbine-condenser-rotator','vent-condenser-rotator'}

def remember(row,reason='Runtime alpha, directional placement, holes and state geometry'):
 p,_=original(row)
 if not any(a['file']==rel(p) for a in geometry):
  geometry.append({'file':rel(p),'sha256':sha(p),'reason':reason+'; retained integration input, not newly painted art.'})

def getmaster(name):
 if name not in cache:cache[name]=master(name)
 return cache[name]

def getbody(row):
 return getmaster(row['blockId'] or row['region'])

def texture_canvas(native,size):
 """Resize real painted pixels; cover uncovered padding with existing jade art.

 Original geometry may include a small corner outside the new silhouette. Such
 corners use a real jade material crop, never palette fills or invented detail.
 """
 q=np.asarray(native.crop(native.getchannel('A').getbbox()).resize(size,Image.Resampling.LANCZOS)).copy()
 good=q[:,:,3]>48
 _,jade=getmaster('liquid-source')
 pad=np.asarray(jade.crop((150,145,210,205)).resize(size,Image.Resampling.LANCZOS))
 q[~good,:3]=pad[~good,:3]
 return q

def material_geometry(native,orig):
 """Keep exact original functional geometry while sampling actual painted texture."""
 q=texture_canvas(native,orig.size);o=np.asarray(orig)
 # Preserve source light/dark state readability without substituting a flat palette.
 light=o[:,:,:3].mean(2)/255
 q[:,:,:3]=np.clip(q[:,:,:3].astype(float)*(.78+.22*light[:,:,None]),0,255).astype('uint8')
 q[:,:,3]=o[:,:,3];q[q[:,:,3]==0]=0
 return Image.fromarray(q)

def aligned_body_alpha(row,orig):
 bodyrow=ROWS[row['blockId']];_,template=original(bodyrow);_,native=getbody(row)
 body=fit(native,template);out=Image.new('RGBA',orig.size)
 out.alpha_composite(body,((orig.width-body.width)//2,(orig.height-body.height)//2))
 return np.asarray(out)[:,:,3]

def effect(row,orig):
 # Original single-edge geometry is intentional for four runtime heat rotations.
 # Keep technical neutral RGB to permit the game's red/liquid/team tinting.
 remember(row)
 a=np.asarray(orig)[:,:,3]
 return neutral_mask(a)

def component_boxes(mask):
 """4-neighbour connected components, used only for existing piston icon layout."""
 mask=mask.copy();out=[];h,w=mask.shape
 for y,x in zip(*np.where(mask)):
  if not mask[y,x]:continue
  stack=[(y,x)];mask[y,x]=False;xs=[];ys=[]
  while stack:
   yy,xx=stack.pop();xs.append(xx);ys.append(yy)
   for dy,dx in [(1,0),(-1,0),(0,1),(0,-1)]:
    ny,nx=yy+dy,xx+dx
    if 0<=ny<h and 0<=nx<w and mask[ny,nx]:mask[ny,nx]=False;stack.append((ny,nx))
  if len(xs)>3:out.append(tuple(map(int,(min(xs),min(ys),max(xs)+1,max(ys)+1))))
 return out

def piston_icon(row,orig,native):
 out=Image.new('RGBA',orig.size);mask=np.asarray(orig)[:,:,3]>24
 sides=8 if row['blockId']=='pyrolysis-generator' else 4
 yy,xx=np.indices(mask.shape);angle=np.arctan2(yy-(orig.height-1)/2,xx-(orig.width-1)/2)
 sectors=np.floor((angle+np.pi/sides)%(2*np.pi)/(2*np.pi/sides)).astype(int)
 boxes=[]
 # Connected original icons are separated into their actual radial piston sectors.
 for i in range(sides):
  ys,xs=np.where(mask&(sectors==i))
  if len(xs):boxes.append(tuple(map(int,(xs.min(),ys.min(),xs.max()+1,ys.max()+1))))
 for box in boxes:
  cx=(box[0]+box[2])/2-orig.width/2;cy=(box[1]+box[3])/2-orig.height/2
  angle=-np.degrees(np.arctan2(cy,cx))-90
  part=native.rotate(float(angle),resample=Image.Resampling.BICUBIC,expand=True)
  layer=fit(part,orig,box);out.alpha_composite(layer)
 return out,boxes

def rotor_blur(base):
 # Premultiplied rotational exposure of the same part; this is not a new frame.
 acc=np.zeros((base.height,base.width,4),float)
 for angle in np.linspace(-17,17,9):
  a=np.asarray(base.rotate(float(angle),resample=Image.Resampling.BICUBIC)).astype(float)/255
  a[:,:,:3]*=a[:,:,3,None];acc+=a/9
 alpha=acc[:,:,3];nz=alpha>0
 acc[nz,:3]/=alpha[nz,None]
 return Image.fromarray(np.clip(acc*255,0,255).astype('uint8'))

def neutral_diode_plate(native):
 """Patch actual jade pixels over the concept's baked arrow, keeping the frame.

 PowerDiode keeps its base fixed and rotates a separate arrow. This local cleanup
 is a pixel derivation, not a newly painted or AI-generated master.
 """
 p,jade=getmaster('liquid-source');sample=jade.crop((150,145,210,205))
 box=native.getchannel('A').getbbox();w=box[2]-box[0];h=box[3]-box[1]
 pts=[(.39,.21),(.61,.21),(.77,.34),(.77,.61),(.63,.72),(.37,.72),(.23,.61),(.23,.34)]
 mask=Image.new('L',native.size);ImageDraw.Draw(mask).polygon([(round(box[0]+x*w),round(box[1]+y*h)) for x,y in pts],fill=255)
 field=sample.resize(native.size,Image.Resampling.LANCZOS);out=native.copy();out.paste(field,(0,0),mask)
 return out

def make(row):
 name=row['region'];bid=row['blockId'];op,orig=original(row)
 # Neutral material/ore masks and the off-centre burst arrow are runtime glyphs.
 technical=(name.startswith('drill-item-') or name.endswith('-liquid') or
  name in {'cultivator-middle','neoplasia-reactor-middle','impact-drill-item','eruption-drill-item',
  'impact-drill-arrow','impact-drill-arrow-blur','eruption-drill-arrow','eruption-drill-arrow-blur'})
 if technical:
  remember(row,'Exact neutral tint mask or off-centre burst indicator geometry')
  return save(row,orig,op,{'kind':'exact_original_runtime_tint_mask_or_burst_glyph',
   'newPaintedDetail':False,'reason':'The renderer tints this neutral stencil and/or places it repeatedly at runtime.'},
   disposition='exact_upstream_technical_reuse')
 if name in ROTORS or name.removesuffix('-blur') in ROTORS:
  rotor=name.removesuffix('-blur');p,native=getmaster(rotor+'-part')
  base=fit(native,orig);out=rotor_blur(base) if name.endswith('-blur') else base
  return save(row,out,p,{'kind':'independent_native_rotor_on_original_canvas',
   'runtimeMotion':'continuous rotation','rotationalExposureDegrees':34 if name.endswith('-blur') else None,
   'blurDerivedFromSameRotor':name.endswith('-blur'),'newPaintedDetail':False})
 if name.endswith('-rotator-bottom'):
  p,native=getmaster(bid+'-rotator-part');out=Image.new('RGBA',orig.size)
  boxes=component_boxes(np.asarray(orig)[:,:,3]>24)
  for box in boxes:out.alpha_composite(fit(native,orig,box))
  remember(row)
  return save(row,out,p,{'kind':'native_rotor_back_teeth_at_original_component_positions','componentBoxes':boxes,
   'runtimeMotion':'wall-contact rotation','newPaintedDetail':False})
 if '-piston' in name:
  part=bid+'-piston-t-part' if name.endswith('-piston-t') else bid+'-piston-part'
  p,native=getmaster(part)
  if name.endswith('-icon'):
   out,boxes=piston_icon(row,orig,native);remember(row)
   operation={'kind':'plan_icon_composed_from_independent_native_pistons','originalComponentBoxes':boxes,
    'runtimeAnimation':False,'newPaintedDetail':False}
  else:
   native=native.rotate(-90,resample=Image.Resampling.BICUBIC,expand=True)
   if name.endswith('1'):native=ImageOps.flip(native)
   out=fit(native,orig)
   operation={'kind':'independent_native_piston_on_original_canvas','localRotationDegrees':-90,
    'oppositeLightVariantVerticalFlip':name.endswith('1'),'runtimeMotion':'DrawPistons translation and rotation',
    'newPaintedDetail':False}
  return save(row,out,p,operation)
 if name in {'phase-weaver-weave','phase-synthesizer-weave','phase-synthesizer-weave-glow'}:
  p,native=getmaster(bid+'-weave-part')
  _,weave_template=original(ROWS[bid+'-weave']);weave=fit(native,weave_template)
  out=Image.new('RGBA',orig.size)
  out.alpha_composite(weave,((orig.width-weave.width)//2,(orig.height-weave.height)//2))
  if name.endswith('-glow'):
   a=np.asarray(out);lum=a[:,:,:3].astype(float).mean(2)/255
   out=neutral_mask((a[:,:,3]*(.25+.75*lum)).astype('uint8'))
  return save(row,out,p,{'kind':'independent_native_weaving_shuttle' if not name.endswith('-glow') else 'new_weave_aligned_neutral_glow',
   'runtimeMotion':'two counter-rotating layers' if bid=='phase-synthesizer' else 'continuous rotation',
   'newPaintedDetail':False})
 if name.startswith('impact-reactor-plasma-'):
  p,native=getmaster('impact-reactor-plasma-part');index=int(name[-1])
  rotated=native.rotate(index*41,resample=Image.Resampling.BICUBIC,expand=False)
  out=fit(rotated,orig);a=np.asarray(out);oa=np.asarray(orig)[:,:,3].astype(float)/255
  # The four source alpha structures are simultaneous rotating additive layers.
  alpha=(a[:,:,3]*(.22+.78*oa)).astype('uint8');out=neutral_mask(alpha);remember(row)
  return save(row,out,p,{'kind':'independent_painted_plasma_ring_with_layer_specific_alpha',
   'layerIndex':index,'localRotationDegrees':index*41,'simultaneouslyDrawnLayers':4,
   'notAnimationFrames':True,'originalAlphaModulatesPaintedRing':True,'newPaintedDetail':False})
 if name==bid+'-top' and bid in CAPS:
  p=ROOT/'full-game/units/parts'/('joint-cap-small.png' if orig.width<=64 else 'joint-cap-heavy.png')
  native=Image.open(p).convert('RGBA');out=fit(native,orig)
  return save(row,out,p,{'kind':'independent_static_hub_cap','originalHubBounds':list(orig.getchannel('A').getbbox()),
   'doesNotReplaceRotorWithWholeBuilding':True,'newPaintedDetail':False})
 if name=='steam-generator-cap':
  p=ROOT/'full-game/units/parts/joint-cap-small.png';native=Image.open(p).convert('RGBA')
  return save(row,fit(native,orig),p,{'kind':'independent_static_turbine_hub_cap','newPaintedDetail':False})
 if name=='diode-arrow':
  p,native=getmaster('bridge-arrow-part')
  return save(row,fit(native,orig),p,{'kind':'independent_right_facing_native_direction_arrow','newPaintedDetail':False})
 if name=='diode':
  p,native=getbody(row)
  return save(row,fit(neutral_diode_plate(native),orig),p,{'kind':'native_diode_fixed_frame_with_baked_direction_removed',
   'localPixelCleanup':'Existing liquid-source jade crop [150,145,210,205] replaces only the inner octagonal plate; outer painted frame remains unchanged.',
   'runtimeDirection':'PowerDiode rotates only its independent diode-arrow region','newPaintedDetail':False},
   extra_sources=[{'file':rel(getmaster('liquid-source')[0]),'sha256':sha(getmaster('liquid-source')[0]),'crop':[150,145,210,205]}])
 p,native=getbody(row)
 drawers=DEFS.get(bid,{}).get('drawerClasses',[])
 hot_top=name==bid+'-top' and any(c in drawers for c in ['DrawWarmupRegion','DrawFlame','DrawFade'])
 suffix=name[len(bid):]
 is_effect=any(suffix.startswith(k) for k in ['-glow','-heat','-lights','-ventglow']) or suffix in {'-rim','-light','-vents'} or hot_top
 # Top1/2 and heater side2 are structural directional variants, not heat masks.
 if is_effect and not re.search(r'-(top[12]|side2)$',name) and name!=bid:
  out=effect(row,orig)
  return save(row,out,p,{'kind':'neutral_effect_mask_with_exact_original_directional_alpha',
   'runtimeTintPreserved':True,'singleSideHeatRotatedPerInput':name.endswith('-heat') and 'DrawHeatInput' in drawers,
   'warmupOverlay':hot_top,'newPaintedDetail':False},disposition='retained_functional_effect_geometry')
 # Any structural sublayer uses a masked sample of real native painted pixels.
 # Bodies placed above liquid, weave, piston or plasma must keep their windows.
 layered_body=name==bid and (bid+'-bottom' in ROWS or bid in {'battery','battery-large'})
 if name!=bid or layered_body:
  out=material_geometry(native,orig);remember(row)
  # Liquid output marks are colored by their asset, not by DrawLiquidOutputs.
  # Preserve the source's material hue contrast while retaining painted texture.
  if '-output' in suffix:
   a=np.asarray(out).copy();o=np.asarray(orig);rgb=o[:,:,:3].astype(float)
   color=rgb/np.maximum(rgb.mean(2)[:,:,None],1)
   a[:,:,:3]=np.clip(a[:,:,:3]*color,0,255).astype('uint8');out=Image.fromarray(a)
  return save(row,out,p,{'kind':'native_painted_texture_through_original_functional_layer_geometry',
   'transparentChannelsPreserved':True,'exactOriginalAlpha':True,'nativeMasterIsTextureSource':True,
   'directionVariant':name[-1] if re.search(r'-(top|output)[12]$',name) else None,
   'paddingMaterial':'Existing liquid-source jade crop [150,145,210,205] fills only areas outside the painted silhouette; no new detail.',
   'liquidOutputHuePreserved':'-output' in suffix,'newPaintedDetail':False},
   disposition='styled_material_with_original_layer_geometry',
   extra_sources=[{'file':rel(getmaster('liquid-source')[0]),'sha256':sha(getmaster('liquid-source')[0]),'crop':[150,145,210,205]}])
 return save(row,fit(native,orig),p,{'kind':'native_building_fitted_to_original_canvas_bounds','newPaintedDetail':False})

def main():
 rows=[]
 for row in OWN:
  rows.append(make(row))
  if len(rows)%40==0:
   write(HERE/'batches/hud-working.json',{'sourceMappings':rows,'status':'in_progress','integrationGeometryInputs':geometry})
   print('exported',len(rows),flush=True)
 result=finish_batch('hud_review',CATEGORIES,rows)
 result['integrationGeometryInputs']=geometry
 result['contacts']=contact(rows,'industry-compat')
 result['codeInputs']=[{'file':rel(p),'sha256':sha(p)} for p in sorted((HERE/'industry-code').glob('*.java'))]
 result['sourceCodeCommit']='17012d61d9e4c3cbd9820d87e81c24495486ac53'
 result['staticReviewPending']=True
 write(HERE/'batches/hud_review.json',result)
 print(json.dumps({'exported':len(rows),'geometryInputs':len(geometry),'contacts':result['contacts']}))

if __name__=='__main__':main()
