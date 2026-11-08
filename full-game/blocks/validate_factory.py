"""Static source-contract audit and actual-pixel assembly inspection aids.

This is not an engine renderer and does not claim an in-game test.
"""
from export_common import *
from export_units import canonical, centered
import argparse,math

BATCH=HERE/'batches/units_air_erekir.json'
m=read(BATCH);rows=m['sourceMappings'];by={a['region']:a for a in rows}
def load(name):return Image.open(ROOT/by[name]['file']).convert('RGBA')
def stamp(canvas,im,angle=0,dx=0,dy=0):
    im=im.rotate(angle,expand=True, resample=Image.Resampling.NEAREST)
    canvas.alpha_composite(im,(round((canvas.width-im.width)/2+dx),round((canvas.height-im.height)/2-dy)))
def panel(images,name):
    cols=4;cell=260;h=240;can=Image.new('RGB',(cols*cell,math.ceil(len(images)/cols)*h),(30,47,46));d=ImageDraw.Draw(can)
    for i,(label,im) in enumerate(images):
        im=ImageOps.contain(im,(236,196),Image.Resampling.NEAREST);x=i%cols*cell;y=i//cols*h
        can.paste(im,(x+(cell-im.width)//2,y+(196-im.height)//2),im);d.text((x+4,y+205),label,fill=(239,230,206))
    p=HERE/'qa'/name;can.save(p);return rel(p)

def main(accept=False):
    errors=[];checks=[]
    for a in rows:
        p=ROOT/a['file'];n=ROOT/a['nativeFile'];im=Image.open(p).convert('RGBA');ar=np.asarray(im);op,o=original(ROWS[a['region']]);oa=np.asarray(o)
        issues=[]
        if sha(p)!=a['sha256'] or sha(n)!=a['nativeSha256']:issues.append('changed_hash')
        if im.size!=o.size:issues.append('canvas')
        if not im.getchannel('A').getbbox() and o.getchannel('A').getbbox():issues.append('unexpected_empty')
        if a['disposition']=='exact_upstream_technical_reuse' and p.read_bytes()!=op.read_bytes():issues.append('changed_technical_reuse')
        if a['disposition']=='styled_material_with_original_runtime_geometry' and not np.array_equal(ar[:,:,3],oa[:,:,3]):issues.append('changed_functional_alpha')
        if a['operation'].get('whiteRgb') and np.any(ar[:,:,:3][ar[:,:,3]>0]!=255):issues.append('nonwhite_tint_mask')
        if a['operation'].get('alphaContainedByNewBody'):
            _,body=canonical(ROWS[a['region']]);body=centered(body,im.size)
            if np.any(ar[:,:,3]>np.asarray(body)[:,:,3]):issues.append('effect_outside_body')
        if a['disposition']=='native_body_aligned_foreground':
            _,body=canonical(ROWS[a['region']]);ba=np.asarray(centered(body,im.size));visible=ar[:,:,3]>0
            if np.any(ar[:,:,3]>ba[:,:,3]) or np.any(ar[:,:,3]>oa[:,:,3]):issues.append('foreground_outside_body_or_occlusion')
            if np.any(ar[:,:,:3][visible]!=ba[:,:,:3][visible]):issues.append('foreground_body_paint_mismatch')
        errors.extend(a['region']+':'+v for v in issues);checks.append(dict(region=a['region'],file=a['file'],sha256=sha(p),issues=issues))
    expected={a['sourcePath'] for a in ROWS.values() if a['category'] in ['payload','units','defense']}
    assert len(rows)==141 and len(by)==141 and {a['sourcePath'] for a in rows}==expected
    assemblies=[];motion=[]
    # PayloadConveyor clips two copies of the same moving chevron over its stationary floor.
    for name in ['payload-conveyor','reinforced-payload-conveyor','payload-router','reinforced-payload-router']:
        body=load(name);top=load(name+'-top');variants=[]
        for phase in range(4):
            out=body.copy();shift=round(body.width*phase/4)
            for dx in [shift,shift-body.width]:out.alpha_composite(top,(dx,0))
            edge=load(name+'-over') if name+'-over' in by else load(name+'-edge')
            if name+'-over' in by:out.alpha_composite(edge)
            else:
                for angle in [90,270]:stamp(out,edge,angle)
            variants.append(np.asarray(out));assemblies.append((name+' phase '+str(phase),out))
        changes=[int(np.any(variants[0]!=v,axis=2).sum()) for v in variants[1:]]
        if not all(n>0 for n in changes):errors.append(name+':motion_hidden')
        motion.append(dict(id=name,comparedPhases=[.25,.5,.75],visibleChangedPixels=changes))
    paths=[panel(assemblies,'factory-belt-motion.png')];assemblies=[];drivers=[]
    # Runtime world units multiply by four source pixels; arm offsets are separate from original canvas offsets.
    for name in ['payload-mass-driver','large-payload-mass-driver']:
        for rotation,cur in [(90,16),(90,32),(0,32),(180,32)]:
            out=Image.new('RGBA',(256,256));stamp(out,load(name+'-base'));stamp(out,load(name+'-top'))
            angle=rotation-90;rad=math.radians(rotation);side=cur/2-8;back=max(cur/2-2.75-89/8,0)
            # trns(rotation,0,-side) gives the right hand offset; subtract for left.
            rx=math.sin(rad)*side;ry=-math.cos(rad)*side;bx=-math.cos(rad)*back;byy=-math.sin(rad)*back
            stamp(out,load(name+'-left'),angle,4*(-rx+bx),4*(-ry+byy))
            stamp(out,load(name+'-right'),angle,4*(rx+bx),4*(ry+byy))
            stamp(out,load(name+'-cap'),angle)
            assemblies.append((name+' r'+str(rotation)+' span'+str(cur),out))
            drivers.append(dict(id=name,rotation=rotation,curSize=cur,leftOffsetPixels=[4*(-rx+bx),4*(-ry+byy)],rightOffsetPixels=[4*(rx+bx),4*(ry+byy)]))
    paths.append(panel(assemblies,'factory-driver-assembly.png'));assemblies=[]
    for name in ['basic-assembler-module','mech-assembler','ship-assembler','tank-assembler']:
        for r in range(4):
            out=Image.new('RGBA',(224,224));stamp(out,load(name));side=load(name+('-side2' if r>=2 else '-side1'))
            # Block.drawSideRegion uses region.width * region.scl(), with 32 px per tile.
            edge=(DEFS[name]['tileSize']*32-side.width)/2 if name=='basic-assembler-module' else 0
            stamp(out,side,r*90,edge*math.cos(r*math.pi/2),edge*math.sin(r*math.pi/2));stamp(out,load(name+'-top'))
            assemblies.append((name+' r'+str(r*90),out))
    paths.append(panel(assemblies,'factory-assembler-directions.png'));assemblies=[]
    for name in ['build-tower','radar','repair-point','repair-turret']:
        for r in range(4):
            out=Image.new('RGBA',(160,160))
            if name+'-base' in by:stamp(out,load(name+'-base'))
            stamp(out,load(name),r*90)
            assemblies.append((name+' head '+str(r*90),out))
    paths.append(panel(assemblies,'factory-rotating-heads.png'))
    usedNative={a['nativeFile']:a for a in rows if '/reference-sprites/' not in a['nativeFile']}
    allNativeContacts=contact([dict(file=k,region=Path(k).stem)for k in sorted(usedNative)],'factory-native-final')
    nativeNames=['unit-factories-01-light','unit-factories-02-dark','support-defense-01-light','payload-and-doors-01-dark','logistics-special-04-light','moving-heads-pistons-02-dark']
    nativeContacts=[{'file':rel(HERE/'qa'/(n+'.jpg')),'sha256':sha(HERE/'qa'/(n+'.jpg'))} for n in nativeNames]
    report=dict(checkedAt=datetime.now(timezone.utc).isoformat(),sourceCount=len(rows),errors=errors,checks=checks,
        sourceCommit='17012d61d9e4c3cbd9820d87e81c24495486ac53',runtimeIntegrationVerified=False,
        scope='Static original-canvas/source hashes/alpha semantics, native contact inspection and CPU composition following documented layer order. Actual engine has not run.',
        payloadConveyorMotion=motion,driverArmOffsets=drivers,
        assemblerRule='UnitAssembler uses source canvas centered and r*90; UnitAssemblerModule drawSideRegion offset is (tileSize*32 - region.width)/2 pixels. Current 160px source and size5 mean zero extra offset.',
        inspectionImages=[{'file':p,'sha256':sha(ROOT/p)} for p in paths],nativeContacts=nativeContacts,
        allUsedNativeContacts=[{'file':p,'sha256':sha(ROOT/p)}for p in allNativeContacts],
        compatContacts=[{'file':p,'sha256':sha(ROOT/p)} for p in m['contacts']],
        sourceCodeEvidence=[{'file':rel(p),'sha256':sha(p)}for p in [HERE/'factory-code/Block.java']+list((ROOT/'records/reference-dynamic-sources').glob('core__src__mindustry__world__blocks__payloads__Payload*.java'))+list((ROOT/'records/reference-dynamic-sources').glob('core__src__mindustry__world__blocks__units__UnitAssembler*.java'))],
        status='passed_static_art_runtime_unverified' if accept and not errors else 'numeric_checks_passed_visual_acceptance_pending' if not errors else 'failed')
    if accept:
        report['actualVisualReview']='All listed current compatibility contacts, native contact sheets and four assembly sheets were opened and visually inspected.'
        report['observations']=['Separate heads rotate without stationary pedestal duplication.', 'Driver arms remain independent and separate at wider payload spans; local right-side mirror is performed once; runtime applies no additional mirror.', 'Four belt phases remain visible above stationary floors and below border strips.', 'Assembler sides retain original geometry and are selected/rotated by the unchanged runtime; no fictional construction arm layers.', 'Neutral tint masks, colored additive force-projector mask, reservoir windows and intentionally blank module top preserve original meaning.', 'Dedicated foreground layers now reuse positioned body pixels intersected with original foreground alpha: no detached old corners or arbitrary material texture is superimposed on the new body.']
        assert not errors,errors
        m['status']='art_export_complete_runtime_unverified';m['staticReviewPending']=False;m['review']='full-game/blocks/qa/factory-review.json';m['reviewedAt']=report['checkedAt']
        for a in m['sourceMappings']:
            a['status']='art_export_complete_runtime_unverified';write(ROOT/a['record'],a)
        write(BATCH,m)
    write(HERE/'qa/factory-review.json',report)
    print(json.dumps({'count':len(rows),'errors':errors,'status':report['status'],'inspectionImages':paths,'allUsedNativeContacts':allNativeContacts}))
    if errors:raise SystemExit(1)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--accept',action='store_true');main(p.parse_args().accept)
