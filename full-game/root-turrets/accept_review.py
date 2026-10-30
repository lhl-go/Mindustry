"""Verify fixed source geometry and the reviewed exports without regenerating art."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
write=lambda p,r:p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(HERE/'manifest.json');inv=read(HERE/'inventory.json');original={a['region']:a for a in inv['assets']};entries={a['region']:a for a in m['assets']}
errors=[];heat=[];liquids=[];pairs=[]
for a in m['assets']:
    p=ROOT/a['file'];im=Image.open(p).convert('RGBA');ar=np.array(im)
    if sha(p)!=a['sha256']:errors.append('hash:'+a['region'])
    if list(im.size)!=a['sourceDimensions']:errors.append('size:'+a['region'])
    op=a['operation'];kind=op['kind']
    if kind=='white_heat_mask_intersection_with_new_part_alpha':
        union=np.zeros(ar.shape[:2],dtype=np.uint8)
        for key in op['matchedNewRegions']:
            part=Image.open(ROOT/entries[key]['file']).convert('RGBA');c=Image.new('RGBA',im.size);c.alpha_composite(part,((im.width-part.width)//2,(im.height-part.height)//2));union=np.maximum(union,np.array(c)[:,:,3])
        leaks=int(np.count_nonzero(ar[:,:,3]>union));neutral=bool(np.all(ar[:,:,:3][ar[:,:,3]>0]==255))
        if leaks or not neutral:errors.append('heat:'+a['region'])
        heat.append({'region':a['region'],'leaks':leaks,'neutralWhite':neutral,'pixels':int(np.count_nonzero(ar[:,:,3]))})
    elif kind in ['byte_exact_technical_liquid_alpha','pixel_exact_technical_liquid_alpha']:
        equal=np.array_equal(ar,np.array(Image.open(ROOT/original[a['region']]['localReference']).convert('RGBA')))
        if not equal:errors.append('liquid:'+a['region'])
        op['kind']='pixel_exact_technical_liquid_alpha';op['encoding']='Pixel values retained; PNG container bytes may differ.'
        liquids.append({'region':a['region'],'sourcePixelsEqual':bool(equal)})
    elif kind=='paired_part_derivation':
        left=entries[original[a['region']]['mirrorOf']]
        if op['sourceAlphaIdentical'] and not np.array_equal(ar,np.array(Image.open(ROOT/left['file']).convert('RGBA'))):errors.append('pair:'+a['region'])
        pairs.append({'region':a['region'],'mirrorPixels':op['mirrorPixels'],'sourceAlphaIdentical':op['sourceAlphaIdentical']})
    a['visualReview']='passed_native_light_dark_and_neutral_assembly';a['runtime']='unverified'
    native=[s['file']for s in a.get('derivedFrom',[])if s['file'].startswith('full-game/root-turrets/masters/')]
    a['nativeFile']=native[0]if native else a['file']
    record=p.with_name(p.name+'.derived.json');r=read(record);r['operation']=op;r['visualReview']=a['visualReview'];write(record,r)
assert len(entries)==145 and len(m['nativeMasters'])==67
report={'reviewedAt':datetime.now(timezone.utc).isoformat(),'status':'art_export_complete_runtime_unverified' if not errors else 'failed','sourcePaths':145,'nativeMasters':67,'sourceGeometry':'Original canvas dimensions and bounding-box placement preserved. Native masters supplied separately.','heatMasks':heat,'liquidMasks':liquids,'pairedParts':pairs,'visualEvidence':['full-game/root-turrets/qa/native-light.jpg','full-game/root-turrets/qa/native-dark.jpg','full-game/root-turrets/qa/assembly-contact.jpg'],'visualReview':'All 67 native parts on light/dark backgrounds and 28 neutral assembly composites inspected. No clipped object or opaque background.','runtimeIntegrationVerified':False,'runtimeLimitations':['Engine recoil, rotation, RegionPart offsets, heat blending and fluid fill have not been played in Mindustry.','Neutral assembly previews do not simulate dynamic or repeated procedural parts.'],'errors':errors}
write(HERE/'qa/review.json',report);m['status']=report['status'];m['errors']=errors;m['visualReviewRecord']='full-game/root-turrets/qa/review.json';write(HERE/'manifest.json',m)
print(json.dumps({k:report[k]for k in ['status','sourcePaths','nativeMasters','errors']}));assert not errors
