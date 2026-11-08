"""Rebuild 141 payload, unit-factory and auxiliary-defense source regions.

Native artwork is fitted without inventing detail. Technical connection patterns
retain upstream geometry and are explicitly recorded as material derivations.
"""
from export_common import *
import re
NAME='units_air_erekir';CATS=['payload','units','defense']
ALLOC=read(HERE/'batches/allocation.json')['workers'][NAME]['sourcePaths']
OWN={k:r for k,r in ROWS.items() if r['sourcePath'] in ALLOC}
BATCH=HERE/'batches'/f'{NAME}.json'
HEADS={n:n+'-head-part' for n in ['build-tower','radar','repair-point','repair-turret']}
DRIVERS=['payload-mass-driver','large-payload-mass-driver']
BELTS=['payload-conveyor','reinforced-payload-conveyor','payload-router','reinforced-payload-router']
GEOMETRY={}

def record_source(p):
    for suffix in ['.derived.json','.generation.json']:
        q=Path(str(p)+suffix)
        if q.exists():return rel(q)
    return None

def remember(row,reason):
    p,_=original(row)
    GEOMETRY[rel(p)]={'file':rel(p),'sha256':sha(p),'reason':reason}

def emit(row,out,source,op,**more):
    rec=save(row,out,source,op,**more)
    rec.update(generationRecord=rec['record'],nativeGenerationRecord=record_source(source),engineNotVerified=True,
        runtimeRules=dict(originalCanvasPreserved=True,pivot='original source canvas center',sourceCodeUnchanged=True))
    write(ROOT/rec['record'],rec)
    return rec

def source_master(row):
    name=row['blockId']
    if not name:
        size=int(re.search(r'-(\d+)',row['region']).group(1))
        name={3:'constructor',5:'large-constructor',7:'exponential-reconstructor',9:'tetrative-reconstructor'}[size]
    if name=='reinforced-payload-router':name='reinforced-payload-router-v2'
    return master(name)

def centered(im,size):
    out=Image.new('RGBA',size)
    out.alpha_composite(im,((size[0]-im.width)//2,(size[1]-im.height)//2))
    return out

def palette(native):
    a=np.asarray(native);rgb=a[:,:,:3].astype(float);opaque=a[:,:,3]>220
    masks=[opaque&(rgb[:,:,1]>rgb[:,:,0]*1.08)&(rgb[:,:,1]>rgb[:,:,2]*.9),
           opaque&(rgb[:,:,0]>rgb[:,:,1]*1.08)&(rgb[:,:,1]>rgb[:,:,2]*1.2),opaque&(rgb.min(2)>165)]
    fallback=np.median(rgb[opaque],axis=0)
    return np.stack([np.median(rgb[m],axis=0) if m.any() else fallback for m in masks])

def material_geometry(native,orig,flat=False):
    a=np.asarray(orig).copy();rgb=a[:,:,:3].astype(float);lum=rgb.mean(2);colors=palette(native)
    idx=np.where(lum<95,0,np.where(lum<170,1,2));base=colors[idx]
    if flat:
        # The stationary floor must not acquire the moving arrow from its concept master.
        paint=colors[0]*(.60+.45*lum/255)[:,:,None]
    else:
        q=np.asarray(native.crop(native.getchannel('A').getbbox()).resize(orig.size,Image.Resampling.LANCZOS)).astype(float)
        texture=np.where((q[:,:,3]>128)[:,:,None],q[:,:,:3],base)
        weight=np.where(lum>220,.3,.7)[:,:,None]
        paint=(texture*weight+base*(1-weight))*(.72+.35*lum/255)[:,:,None]
    a[:,:,:3]=np.clip(paint,0,255).astype('uint8');a[a[:,:,3]==0]=0
    return Image.fromarray(a)

def structural(row,role,flat=False):
    p,im=source_master(row);_,orig=original(row)
    remember(row,'Exact upstream alpha, holes, offsets and structural shade geometry used by '+role)
    return emit(row,material_geometry(im,orig,flat),p,
        dict(type='painted_material_with_original_runtime_geometry',role=role,originalAlphaPreservedExactly=True,
             originalOffsetPreserved=True,newPaintedDetail=False,nativeMasterIsDesignMaterialSource=True,flatStationarySurface=flat),
        disposition='styled_material_with_original_runtime_geometry')

def detached(row,part,angle=0,mirror=False,role=None):
    p,im=master(part);_,orig=original(row)
    if angle:im=im.rotate(angle,expand=True)
    if mirror:im=ImageOps.mirror(im)
    return emit(row,fit(im,orig),p,dict(type='independent_native_part_original_canvas',part=part,role=role,
        localRotationDegrees=angle,localMirrorX=mirror,originalAlphaBoundsPlacement=True,
        runtimeRotationAppliedSeparately=True,newPaintedDetail=False))

def canonical(row):
    name=row['blockId'];_,orig=original(ROWS[name])
    if name in HEADS:
        p,im=master(HEADS[name])
        if name!='radar':im=im.rotate(180,expand=True)
    else:p,im=source_master(row)
    if name=='regen-projector':return p,material_geometry(im,orig)
    return p,fit(im,orig)

def shader(row,colored=False):
    p,body=canonical(row);_,orig=original(row);body=centered(body,orig.size)
    a=np.asarray(body);rgb=a[:,:,:3].astype(float);r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2]
    team='team' in row['region']
    chosen=((g>r*1.04)&(g>b*.85)&(g>55)) if team else ((r>g*.95)&(g>b*1.1)&(g>100))
    alpha=np.where(chosen&(a[:,:,3]>32),a[:,:,3],0).astype('uint8')
    assert np.count_nonzero(alpha)>0,row['region']
    out=np.asarray(neutral_mask(alpha)).copy()
    if colored:
        oa=np.asarray(orig);visible=oa[:,:,3]>0
        tint=np.percentile(oa[:,:,:3][visible],75,axis=0).astype('uint8');out[alpha>0,:3]=tint
        remember(row,'Original additive glow color sampled because this renderer supplies no draw tint')
    return emit(row,Image.fromarray(out),p,dict(type='new_component_aligned_effect_mask',whiteRgb=not colored,
        colorRule='original additive glow palette' if colored else 'white for runtime tint',alphaContainedByNewBody=True,
        selection='jade material' if team else 'warm-gold painted highlights',followsHeadRotation=row['blockId'] in HEADS,
        newPaintedDetail=False),disposition='new_body_aligned_technical_mask')

def aligned_foreground(row):
    """Reuse the actual positioned body pixels for the foreground occlusion layer."""
    p,body=canonical(row);_,orig=original(row);body=centered(body,orig.size)
    a=np.asarray(body).copy();a[:,:,3]=np.minimum(a[:,:,3],np.asarray(orig)[:,:,3]);a[a[:,:,3]==0]=0
    remember(row,'Original foreground occlusion alpha intersected with positioned new body; preserves its design and avoids detached old corner geometry')
    return emit(row,Image.fromarray(a),p,dict(type='native_body_foreground_occlusion_layer',
        bodyPixelsUnchanged=True,alphaLimitedToBodyAndOriginalForeground=True,newPaintedDetail=False,
        role='foreground over payload; same positioned paint as stationary body'),disposition='native_body_aligned_foreground')

def make(row):
    name=row['region'];block=row['blockId'];op,orig=original(row)
    if name in ['target-dummy-tether','target-dummy-tether-end','regen-projector-mid','basic-assembler-module-top']:
        remember(row,'Neutral laser end/line or legacy soft effect texture; exact technical reuse')
        return emit(row,orig,op,dict(type='exact_upstream_neutral_technical_texture',newPaintedDetail=False),disposition='exact_upstream_technical_reuse')
    if name=='unit-cargo-unload-point-top':
        p,body=canonical(row);body=centered(body,orig.size)
        alpha=np.minimum(np.asarray(orig)[:,:,3],np.asarray(body)[:,:,3])
        remember(row,'Original item-color indicator alpha clipped to the replacement building')
        return emit(row,neutral_mask(alpha),p,dict(type='new_component_aligned_effect_mask',whiteRgb=True,
            alphaContainedByNewBody=True,colorRule='Draw.color(item.color)',newPaintedDetail=False),disposition='new_body_aligned_technical_mask')
    if name in HEADS:
        return detached(row,HEADS[name],angle=0 if name=='radar' else 180,
            role='independent rotating head; visible nozzle corrected to source +Y direction' if name!='radar' else 'independent scan dish')
    if name in ['build-tower-base','radar-base','repair-point-base']:
        p=ROOT/'full-game/units/parts/mech-base-heavy.png';im=Image.open(p).convert('RGBA')
        return emit(row,fit(im,orig),p,dict(type='stationary_native_pedestal',containsRotatingHead=False,newPaintedDetail=False))
    if block in DRIVERS:
        suffix=name.removeprefix(block)
        if suffix=='':return detached(row,block+'-head-part',role='icon/placement/shadow silhouette; runtime colored assembly uses separate arms and cap')
        if suffix in ['-left','-right']:
            return detached(row,block+'-left-part',mirror=suffix=='-right',role='independently translated arm; right mirrored once locally; runtime does not mirror')
        if suffix=='-cap':return detached(row,block+'-cap-part',role='independent rotating cap, original offset retained')
        if suffix=='-base':return structural(row,'fixed base below moving assembly',flat=True)
        if suffix=='-top':return structural(row,'fixed top frame above payload and below moving assembly')
    if name in BELTS:return structural(row,'stationary belt/router floor without a painted directional arrow',flat=True)
    if name.startswith('factory-'):return structural(row,'shared PayloadBlock fallback '+name)
    if name=='regen-projector':return structural(row,'hydrogen reservoir frame; original liquid windows remain open')
    if name=='regen-projector-bottom':return structural(row,'fixed reservoir floor under DrawLiquidTile',flat=True)
    if name=='force-projector-top':return shader(row,colored=True)
    if any(s in name for s in ['-team','-glow','-heat']) or name in ['mender-top','mend-projector-top','overdrive-projector-top','overdrive-dome-top']:
        return shader(row)
    if name.endswith('-top') and block not in BELTS:return aligned_foreground(row)
    if name.endswith(('-top','-edge','-over','-side1','-side2')):
        return structural(row,'moving conveyor chevrons' if block in BELTS and name.endswith('-top') else
            'fixed router border' if name.endswith('-over') else
            'rotation-selected assembler side; runtime controls side1/side2 and orientation' if '-side' in name else
            'fixed top frame / original connection edge')
    p,im=source_master(row)
    return emit(row,fit(im,orig),p,dict(type='native_body_original_canvas_export',
        role='complete icon or placement preview' if name.endswith(('-icon','-preview')) else 'stationary native building body',newPaintedDetail=False))

def main():
    records=[]
    for row in OWN.values():
        records.append(make(row))
        if len(records)%16==0:
            write(BATCH,dict(ownerBatch=NAME,categories=CATS,sourceCount=len(records),expectedCount=len(OWN),status='in_progress',sourceMappings=records,runtimeIntegrationVerified=False))
    result=finish_batch(NAME,CATS,records)
    result['integrationGeometryInputs']=list(GEOMETRY.values())
    result['contacts']=contact(records,'units-payload-defense-compat')
    write(BATCH,result)
    print(json.dumps({'exported':len(records),'geometryInputs':len(GEOMETRY),'contacts':result['contacts']}))

if __name__=='__main__':main()
