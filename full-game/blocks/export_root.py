"""Export the root-owned transport, liquid, logic, wall, core and sandbox paths."""
from export_common import *
import re,shutil
CATEGORIES=['distribution','liquid','logic','walls','storage','campaign','sandbox']
OWN=[a for a in ROWS.values()if a['category']in CATEGORIES]
technical={'center','cross','cross-full','arrow-glow','fluid','unloader-center','duct-unloader-center'}
geometry=[]
base_save=save
def save(row,out,native,operation,**kwargs):
 if Path(native).stem in ['plastanium-conveyor','surge-conveyor']:
  operation={**operation,'nativeMaterialRotationBeforePlacement':-90,'orientationReason':'StackConveyor rotation=0 points east; original concept belt axis points north.'}
 return base_save(row,out,native,operation,**kwargs)
def remember(row):
 p,_=original(row)
 a={'file':rel(p),'sha256':sha(p),'reason':'Required original alpha/connection/state geometry input to the documented material derivation; not newly painted art.'}
 if a not in geometry:geometry.append(a)
def getmaster(name):
 aliases={'large-canvas':'canvas','reinforced-payload-router':'reinforced-payload-router-v2'}
 name=aliases.get(name,name)
 if name=='mass-driver-base':
  p=ROOT/'full-game/units/parts/mech-base-heavy.png';return p,Image.open(p).convert('RGBA')
 derived=HERE/'masters-derived'/(name+'.png')
 if derived.exists():return derived,Image.open(derived).convert('RGBA')
 p,im=master(name)
 if name in ['plastanium-conveyor','surge-conveyor']:im=im.rotate(-90,expand=True)
 return p,im
def blockmaster(row):
 name=row['blockId']or row['region'].removesuffix('-top')
 if name=='mass-driver':name='mass-driver-base'
 if name.startswith('scrap-wall'):name='scrap-wall'
 if name.endswith('-large')and not(HERE/'masters'/(name+'.png')).exists():name=name[:-6]
 if name=='large-canvas':name='canvas'
 return getmaster(name)
def palette(im):
 a=np.asarray(im);rgb=a[:,:,:3];opaque=a[:,:,3]>180
 jade=opaque&(rgb[:,:,1]>rgb[:,:,0]*1.08)&(rgb[:,:,1]>rgb[:,:,2]*.9)
 gold=opaque&(rgb[:,:,0]>rgb[:,:,1]*1.08)&(rgb[:,:,1]>rgb[:,:,2]*1.2)
 light=opaque&(rgb.min(2)>165)
 fallback=np.median(rgb[opaque],axis=0)
 return [np.median(rgb[m],axis=0)if m.any()else fallback for m in [jade,gold,light]]
def material_geometry(native,orig):
 """Retain exact official joins/holes/state pattern; apply sampled AI material and shading."""
 a=np.asarray(orig).copy();rgb=a[:,:,:3].astype(float);lum=rgb.mean(2);colors=palette(native)
 q=np.asarray(native.crop(native.getchannel('A').getbbox()).resize(orig.size,Image.Resampling.LANCZOS)).astype(float)
 # Fine variation comes only from actual painted pixels. Geometry is the original input.
 idx=np.where(lum<95,0,np.where(lum<170,1,2))
 base=np.stack(colors)[idx]
 texture=np.where((q[:,:,3]>128)[:,:,None],q[:,:,:3],base)
 # Retain actual hand-painted texture wherever available; neutral state symbols keep contrast.
 weight=np.where(lum>220,.3,.7)[:,:,None]
 paint=(texture*weight+base*(1-weight))*(.72+.35*(lum/255))[:,:,None]
 a[:,:,:3]=np.clip(paint,0,255).astype('uint8');a[a[:,:,3]==0]=0;return Image.fromarray(a)
def aligned_body(name,size):
 row=ROWS.get(name)
 if row:
  _,orig=original(row);p,im=blockmaster(row);body=fit(im,orig)
 else:
  p,im=getmaster(name);body=fit(im,Image.new('RGBA',size,(255,255,255,255)))
 out=Image.new('RGBA',size);out.alpha_composite(body,((size[0]-body.width)//2,(size[1]-body.height)//2));return out
def neutral_aligned(row,orig,mode):
 body=aligned_body(row['blockId'],orig.size);a=np.asarray(body);rgb=a[:,:,:3].astype(float)
 if mode=='team':
  mask=(rgb[:,:,1]>rgb[:,:,0]*1.10)&(rgb[:,:,1]>rgb[:,:,2]*.9)&(a[:,:,3]>100)
  yy,xx=np.indices(mask.shape);cx=orig.width/2;cy=orig.height/2
  mask&=(abs(xx-cx)<orig.width*.38)&(abs(yy-cy)<orig.height*.38)
  if not mask.any():mask=np.asarray(orig)[:,:,3]>0
  alpha=np.where(mask,a[:,:,3],0).astype('uint8')
 else:alpha=np.minimum(np.asarray(orig)[:,:,3],a[:,:,3])
 return neutral_mask(alpha)
def make(row):
 name=row['region'];_,orig=original(row)
 # Neutral tints, fluid stencil and mathematical connection bases must keep their semantics.
 if name in technical or name.startswith('conduit-bottom')or name.endswith('-liquid')or '-bridge-liquid'in name:
  op,_=original(row);remember(row)
  return save(row,orig,op,{'kind':'exact_original_neutral_alpha_or_fluid_input','newPaintedDetail':False},disposition='exact_upstream_technical_reuse')
 conveyor=re.fullmatch(r'(armored-conveyor|titanium-conveyor|conveyor)-(\d)-(\d)',name)
 conduit=re.fullmatch(r'(armored-duct|duct|conduit|pulse-conduit|plated-conduit|reinforced-conduit)-top-(\d)',name)
 if conveyor or conduit:
  g=conveyor or conduit;family,index=g.group(1),g.group(2);p,im=getmaster(family+'-shape-'+index)
  out=material_geometry(im,orig);remember(row)
  return save(row,out,p,{'kind':'painted_material_with_exact_official_connection_and_phase_geometry','connectionIndex':int(index),'animationFrame':int(g.group(3))if conveyor else None,'topLayerUsesOriginalTransparentChannels':bool(conduit),'newPaintedDetail':False,'nativeMasterIsDesignMaterialSource':True},disposition='styled_material_with_original_connection_geometry')
 # Dynamic head and detached cargo/launch/core parts have their own native art.
 special={'mass-driver':'mass-driver-head-part','mass-driver-base':'mass-driver-base','launchpod':'launchpod-part','advanced-launch-pad-pod':'advanced-launch-pad-pod-part','plastanium-conveyor-stack':'plastanium-conveyor-stack-part','surge-conveyor-stack':'surge-conveyor-stack-part','source-bottom':'source-bottom-part','thruster':'thruster-base','thruster-top':'thruster-top'}
 if name in special:
  p,im=getmaster(special[name]);return save(row,fit(im,orig),p,{'kind':'independent_native_part_fitted_to_original_canvas_and_bounds','part':special[name],'newPaintedDetail':False})
 if '-thruster'in name and name.startswith('core-'):
  size='small'if row['blockId']in ['core-shard','core-bastion']else'medium'if row['blockId']in ['core-foundation','core-citadel']else'large'
  p,im=getmaster('core-thruster-'+size+'-part')
  if size=='large':im=ImageOps.mirror(im)
  if name.endswith('2'):im=ImageOps.flip(im)
  return save(row,fit(im,orig),p,{'kind':'independent_thruster_bracket_original_offset','oppositeCornerVariant':name[-1],'localHorizontalMirror':size=='large','localVerticalMirror':name.endswith('2'),'nativeNozzlesAlignedEastBeforeRuntimeQuarterTurns':True,'sourceBoundsUsedForPlacement':True,'newPaintedDetail':False})
 if name.endswith('-arrow')or name in ['bridge-arrow','duct-bridge-dir','reinforced-bridge-conduit-dir']:
  p,im=getmaster('bridge-arrow-part');return save(row,fit(im,orig),p,{'kind':'native_right_facing_arrow_original_bounds','newPaintedDetail':False})
 # Building body variants share identity, but keep their original dimensions and pivots.
 if name.endswith('-open'):
  p,im=getmaster(name[:-5]);out=material_geometry(im,orig);remember(row)
  return save(row,out,p,{'kind':'painted_door_material_on_exact_original_open_frame_geometry','centerRemainsTransparent':True,'nativeMasterIsDesignMaterialSource':True,'newPaintedDetail':False},disposition='styled_open_frame_with_original_passage_geometry')
 if name.endswith('-team'):
  p,im=blockmaster(row);return save(row,neutral_aligned(row,orig,'team'),p,{'kind':'white_team_mask_selected_from_new_jade_body','alphaLimitedToNewBody':True,'newPaintedDetail':False},disposition='new_body_aligned_technical_mask')
 if any(k in name for k in ['-glow','-heat'])or name.endswith('-light'):
  p,im=blockmaster(row);out=neutral_aligned(row,orig,'glow');remember(row)
  return save(row,out,p,{'kind':'neutral_original_effect_alpha_clipped_to_new_body','newPaintedDetail':False},disposition='new_body_aligned_technical_mask')
 # LiquidRouter draws fluid underneath its region; keep its exact holes and opaque exterior.
 if row['category']=='liquid'and name+'-bottom'in ROWS:
  p,im=blockmaster(row);out=material_geometry(im,orig);remember(row)
  return save(row,out,p,{'kind':'painted_material_on_original_liquid_window_frame','originalLiquidWindowsAndExteriorOcclusionPreserved':True,'newPaintedDetail':False,'nativeMasterIsDesignMaterialSource':True},disposition='styled_material_with_original_liquid_window_geometry')
 # Generic state, edge, top, bottom, display-border and bridge segment geometry.
 structural=any(k in name for k in ['-top','-bottom','-edge','-cap','-side','-corner','-end','-bridge','-on','-center'])or bool(re.fullmatch(r'tile-logic-display-\d+',name))or bool(re.fullmatch(r'(plastanium|surge)-conveyor-\d',name))
 if structural and not(HERE/'masters'/(name+'.png')).exists():
  if name.startswith('duct-bottom'):p,im=getmaster('duct-shape-'+(name[-1]if name[-1].isdigit()else'0'))
  elif name.startswith(('plated-conduit-cap','reinforced-conduit-cap')):p,im=getmaster(name.split('-cap')[0]+'-shape-0')
  elif any(name.startswith(prefix)for prefix in ['bridge-conveyor-','phase-conveyor-','duct-bridge-','bridge-conduit-','phase-conduit-','reinforced-bridge-conduit-']):
   family=next(f for prefix,f in [('bridge-conveyor-','conveyor'),('phase-conveyor-','titanium-conveyor'),('duct-bridge-','duct'),('bridge-conduit-','conduit'),('phase-conduit-','pulse-conduit'),('reinforced-bridge-conduit-','reinforced-conduit')]if name.startswith(prefix))
   p,im=getmaster(family+'-shape-0')
  else:p,im=blockmaster(row)
  out=material_geometry(im,orig);remember(row)
  if name in ['underflow-duct-top','liquid-overflow-gate-top']:
   body=aligned_body(row['blockId']or name.removesuffix('-top'),orig.size);bounds=body.getchannel('A').getbbox();out=fit(out,orig,box=bounds)
   return save(row,out,p,{'kind':'painted_original_indicator_fitted_inside_new_body_bounds','bodyBounds':list(bounds),'canvasAndPivotUnchanged':True,'newPaintedDetail':False,'nativeMasterIsDesignMaterialSource':True},disposition='styled_body_aligned_direction_indicator')
  return save(row,out,p,{'kind':'painted_material_with_original_layer_or_state_geometry','transparentChannelsPreserved':True,'newPaintedDetail':False,'nativeMasterIsDesignMaterialSource':True},disposition='styled_material_with_original_layer_geometry')
 p,im=blockmaster(row)
 if name.startswith('scrap-wall'):
  m=re.search(r'(\d+)$',name)
  if m:im=im.rotate(90*(int(m.group(1))%4),expand=True)
 out=fit(im,orig)
 return save(row,out,p,{'kind':'native_identity_fitted_to_original_canvas_bounds','variantSharesAcceptedIdentity':name!=Path(p).stem,'newPaintedDetail':False})
def main():
 rows=[];pending=[]
 for row in OWN:
  try:rows.append(make(row))
  except AssertionError as e:
   if str(e).startswith('Missing native master'):pending.append({'region':row['region'],'reason':str(e)})
   else:raise
  if len(rows)%40==0:write(HERE/'batches/root-working.json',{'sourceMappings':rows,'pending':pending,'status':'in_progress'})
 write(HERE/'batches/root-working.json',{'sourceMappings':rows,'pending':pending,'status':'in_progress','integrationGeometryInputs':geometry})
 if pending:print(json.dumps({'exported':len(rows),'pending':pending}));return
 result=finish_batch('root',CATEGORIES,rows);result['integrationGeometryInputs']=geometry;result['contacts']=contact(rows,'root-compat');write(HERE/'batches/root.json',result)
 print(json.dumps({'exported':len(rows),'geometryInputs':len(geometry),'contacts':result['contacts']}))
if __name__=='__main__':main()
