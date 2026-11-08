"""Native region extraction plus original-canvas exports; no new imagery is drawn in code."""
import json,hashlib,sys,shutil,re
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image,ImageOps,ImageDraw
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parent
sys.path.insert(0,str(ROOT/'records'))
from pixel_tools import components
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inv=read(HERE/'inventory.json');entries={a['region']:a for a in inv['assets']};masters={};exports={};records=[]
def rec_for(p):
    for suffix in ['.derived.json','.generation.json']:
        q=p.with_name(p.name+suffix)
        if q.exists():return q.relative_to(ROOT).as_posix()
def origin(p):return {'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'record':rec_for(p)}
def save(im,path,sources,operation,region):
    path.parent.mkdir(parents=True,exist_ok=True);im.save(path)
    r={'region':region,'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'size':list(im.size),'derivedAt':datetime.now(timezone.utc).isoformat(),'derivedFrom':[origin(p)for p in sources],'operation':operation,'actualModel':None,'actualQuality':None,'runtime':'unverified','visualReview':'pending'}
    path.with_name(path.name+'.derived.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return r
for batch in read(HERE/'batches.json'):
    n=batch['batch'];cols,rows=batch['grid'];source=HERE/'source'/f'{n:02d}-regions.png';rgba=np.array(Image.open(source).convert('RGBA'));h,w=rgba.shape[:2];alpha=rgba[:,:,3];cells=[[]for _ in range(cols*rows)]
    for group in components(alpha>=16,min_area=28):
        x0,y0,x1,y1=group['bbox'];idx=min(rows-1,int((y0+y1)/2*rows/h))*cols+min(cols-1,int((x0+x1)/2*cols/w));cells[idx].append(group)
    for i,name in enumerate(batch['regions']):
        mask=np.zeros((h,w),dtype=bool)
        for g in cells[i]:
            for y,x0,x1 in g['runs']:mask[y,x0:x1]=True
        assert mask.sum()>100,name
        clean=rgba.copy();clean[:,:,3]=np.clip(np.rint((alpha.astype(float)-8)*255/237),0,255).astype(np.uint8);clean[~mask]=0
        im=Image.fromarray(clean);bbox=im.getbbox();im=im.crop(bbox);out=Image.new('RGBA',(im.width+24,im.height+24));out.alpha_composite(im,(12,12));path=HERE/'masters'/f'{name}.png'
        r=save(out,path,[source],{'kind':'authorized_alpha_component_crop_padding','grid':[cols,rows],'cell':i,'sourceBox':list(bbox),'alphaCutoff':16,'minimumComponentArea':28,'alphaRemap':'clip(round((alpha-8)*255/237),0,255)','retainedRGBUnchanged':True,'resampling':False,'padding':12},name);masters[name]=r
def from_master(entry,master,mirror=False):
    size=tuple(entry['sourceDimensions']);box=entry['sourceAlphaBounds'];im=Image.open(master).convert('RGBA');im=im.crop(im.getbbox())
    if mirror:im=ImageOps.mirror(im)
    # Original atlas canvas and alpha bounding box carry the offset used by RegionPart.
    im=im.resize((box[2]-box[0],box[3]-box[1]),Image.Resampling.LANCZOS);out=Image.new('RGBA',size);out.alpha_composite(im,(box[0],box[1]));return out
def export(entry,im,sources,operation):
    path=HERE/'compat'/entry['sourcePath'];r=save(im,path,sources,operation,entry['region']);r.update(sourcePath=entry['sourcePath'],sourceGitBlob=entry['sourceGitBlob'],sourceDimensions=entry['sourceDimensions'],sourceAlphaBounds=entry['sourceAlphaBounds'],plan=entry['plan']);records.append(r);exports[entry['region']]=r;return r
for name,a in entries.items():
    if name in masters:
        p=ROOT/masters[name]['file'];im=from_master(a,p)
        export(a,im,[p,ROOT/a['localReference']],{'kind':'fit_generated_region_to_original_alpha_bounds','resampling':'LANCZOS','targetBox':a['sourceAlphaBounds'],'canvasPivot':'unchanged center','nativeMasterSize':masters[name]['size'],'requiresRuntimeCalibration':True})
for name,a in entries.items():
    if a['plan']=='mirror_generated_left_part':
        key=a['mirrorOf'];p=ROOT/masters[key]['file'];left=entries[key]
        same=np.array_equal(np.array(Image.open(ROOT/left['localReference']).convert('RGBA'))[:,:,3],np.array(Image.open(ROOT/a['localReference']).convert('RGBA'))[:,:,3])
        im=from_master(a,p,mirror=not same)
        export(a,im,[p,ROOT/a['localReference'],ROOT/left['localReference']],{'kind':'paired_part_derivation','mirrorPixels':not same,'sourceAlphaIdentical':same,'reason':'RegionPart.java loads -r and -l with the same geometry then applies Draw.xscl sign for the second side. No pre-mirror when source alpha is identical. Duo separate barrels use opposite canvas bounds.','resampling':'LANCZOS','targetBox':a['sourceAlphaBounds']})
    elif a['plan']=='translate_generated_cyclone_barrel_1':
        p=ROOT/masters[a['deriveFrom']]['file'];im=from_master(a,p);export(a,im,[p,ROOT/a['localReference']],{'kind':'shared_barrel_fit_to_original_position','resampling':'LANCZOS','targetBox':a['sourceAlphaBounds']})
    elif a['plan']=='retain_white_liquid_fill_mask_aligned_to_canvas':
        p=ROOT/a['localReference'];im=Image.open(p).convert('RGBA');export(a,im,[p],{'kind':'pixel_exact_technical_liquid_alpha','reason':'DrawTurret.drawTurret uses Drawf.liquid with actual fluid color and fill amount; neutral exact reservoir alpha is required. Geometry remains fixed original canvas. PNG encoding bytes may differ.'})
for name,a in entries.items():
    if a['plan']!='derive_heat_mask_from_new_art':continue
    stem=re.sub(r'-(?:glow-)?heat(?:_full)?$','',name)
    candidates=[stem,stem+'-r',stem+'-l']
    keys=[k for k in candidates if k in exports]
    if not keys and a['blockId']in exports:keys=[a['blockId']]
    assert keys,('unmatched heat',name)
    ori=Image.open(ROOT/a['localReference']).convert('RGBA');oa=np.array(ori)[:,:,3];combined=np.zeros(oa.shape,dtype=np.uint8)
    for k in keys:
        im=Image.open(ROOT/exports[k]['file']).convert('RGBA')
        if im.size!=ori.size:
            canvas=Image.new('RGBA',ori.size);canvas.alpha_composite(im,((ori.width-im.width)//2,(ori.height-im.height)//2));im=canvas
        combined=np.maximum(combined,np.array(im)[:,:,3])
    alpha=np.minimum(oa,combined);assert np.count_nonzero(alpha)>0,('empty heat',name)
    result=np.full((*alpha.shape,4),255,dtype=np.uint8);result[:,:,3]=alpha;result[alpha==0,:3]=0;im=Image.fromarray(result)
    export(a,im,[ROOT/a['localReference'],*[ROOT/exports[k]['file']for k in keys]],{'kind':'white_heat_mask_intersection_with_new_part_alpha','reason':'RegionPart and DrawTurret render this neutral alpha additively with runtime heat color; intersecting with actual new part avoids glow on detached empty pixels.','matchedNewRegions':keys,'newArtwork':False,'alphaPixels':int(np.count_nonzero(alpha))})
def composite_for(block_id,size,include_base=False):
    out=Image.new('RGBA',size);used=[]
    names=[n for n,a in entries.items()if a['blockId']==block_id and n in exports and not n.endswith('-preview') and a['role']!='heat-mask' and not n.endswith('-liquid')]
    # Paired -l regions are mirrored by the renderer, not stored in mirror position.
    def order(n):
        if n==block_id:return 0
        if n.endswith('-top'):return 4
        if any(s in n for s in ['back','side','spine']):return 1
        return 2
    for n in sorted(names,key=order):
        im=Image.open(ROOT/exports[n]['file']).convert('RGBA')
        if n.endswith('-l')and n[:-1]+'r'in entries and n!='duo-barrel-l':im=ImageOps.mirror(im)
        out.alpha_composite(im,((size[0]-im.width)//2,(size[1]-im.height)//2));used.append(ROOT/exports[n]['file'])
    return out,used
for name,a in entries.items():
    if a['plan']=='assemble_new_parts_in_source_canvas':
        im,used=composite_for(a['blockId'],tuple(a['sourceDimensions']));assert used
        export(a,im,used,{'kind':'new_region_layer_composite','pose':'original-canvas neutral overlay; runtime offset/recoil and repeated procedural part instances remain consumer controlled','rendererEvidence':'full-game/root-turrets/reference/RegionPart.java','includesBase':False,'newArtwork':False})
assert len(exports)==145,(len(exports),set(entries)-set(exports))
errors=[]
for a in records:
    im=Image.open(ROOT/a['file']);im.verify();im=Image.open(ROOT/a['file'])
    if list(im.size)!=a['sourceDimensions']:errors.append('dimensions:'+a['region'])
    if im.getbbox()is None:errors.append('empty:'+a['region'])
    if sha(ROOT/a['file'])!=a['sha256']:errors.append('hash:'+a['region'])
    for s in a['derivedFrom']:
        if sha(ROOT/s['file'])!=s['sha256']:errors.append('source_hash:'+a['region'])
report={'schemaVersion':1,'status':'exported_pending_visual_review','requiredSourcePaths':145,'exportedSourcePaths':len(records),'uniqueNativeMasters':len(masters),'turretIds':28,'errors':errors,'assets':records,'nativeMasters':list(masters.values()),'runtimeIntegrationVerified':False}
(HERE/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Contact sheets show actual cleaned native parts and assembled source-canvas previews.
for bg,label in [('#efe7d8','light'),('#182d2e','dark')]:
    canvas=Image.new('RGB',(1440,((len(masters)+7)//8)*180),bg);d=ImageDraw.Draw(canvas)
    for i,(n,r)in enumerate(masters.items()):
        im=Image.open(ROOT/r['file']);im.thumbnail((162,140),Image.Resampling.LANCZOS);x=i%8*180;y=i//8*180;canvas.paste(im,(x+(180-im.width)//2,y+5),im);d.text((x+7,y+153),n,fill='#173b35'if label=='light'else'#efdfc3')
    canvas.save(HERE/'qa'/f'native-{label}.jpg',quality=96)
canvas=Image.new('RGB',(1400,4*240),'#e8e1d1');d=ImageDraw.Draw(canvas);assemblies=[]
for i,block in enumerate(inv['blocks']):
    n=block['id'];size=max([max(a['sourceDimensions'])for a in entries.values()if a['blockId']==n]);basekey=('reinforced-'if 'reinforced-'in block['definition']else'')+'block-'+str(block['tileSize'])
    out=Image.new('RGBA',(size,size))
    if basekey in exports:
        base=Image.open(ROOT/exports[basekey]['file']);out.alpha_composite(base,((size-base.width)//2,(size-base.height)//2))
    im,used=composite_for(n,(size,size));out.alpha_composite(im)
    path=HERE/'qa'/f'assembly-{n}.png';out.save(path);assemblies.append({'id':n,'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'pose':'neutral canvas composite, runtime transforms unverified'})
    out.thumbnail((178,190));out=out.resize((min(178,out.width*3),min(190,out.height*3)),Image.Resampling.NEAREST);x=i%7*200;y=i//7*240;canvas.paste(out,(x+(200-out.width)//2,y+8),out);d.text((x+10,y+210),n,fill='#183b35')
canvas.save(HERE/'qa/assembly-contact.jpg',quality=96)
(HERE/'qa/assembly-index.json').write_text(json.dumps(assemblies,indent=2)+'\n')
print(json.dumps({'uniqueNativeMasters':len(masters),'sourcePaths':len(exports),'errors':errors}))
assert not errors
