from pathlib import Path
import json,hashlib,datetime,sys
from PIL import Image
import numpy as np
from inspect_components import components

ROOT=Path(__file__).resolve().parents[3]
OWN=ROOT/'units/serpulo-ground-naval'
REC=ROOT/'records/workers/serpulo-ground-naval'
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=read(OWN/'manifest.json'); assert len(m['assets'])==25
qa=[];current={}
for a in m['assets']:
    p=ROOT/a['file'];assert sha(p)==a['sha256'];assert (ROOT/a['generationRecord']).is_file()
    for layer in a['layers']:
        lp=ROOT/layer['file'];assert lp.is_file() and sha(lp)==layer['sha256'];assert (ROOT/layer['generationRecord']).is_file();current[layer['file']]=layer
        if layer['role'] in ['leg_upper','leg_lower']:
            layer['engineTextureAxisNote']='Native artwork long axis is vertical. Mindustry Lines.line expects the strip along X: atlas adapter must quarter-turn this part; placement data here is image-space and is not engine-tested.'
        if layer['role']=='weapon':
            layer['rotationEvidence']='Separately authored mount. Explicit source rotate properties are retained where shown; inherited weapon-subclass defaults and engine response remain unverified.'
    current[a['file']]=a
    im=Image.open(p);al=np.asarray(im)[:,:,3];cs=components(al>=16)
    q=dict(id=a['id'],sha256=a['sha256'],size=list(im.size),alphaRange=[int(al.min()),int(al.max())],substantialConnectedComponents=sum(c[4]>8 for c in cs),tinyDetachedPixels=sum(c[4] for c in cs if c[4]<=8),clearBorder=bool(all(not np.any(e) for e in [al[0],al[-1],al[:,0],al[:,-1]])),visualReview='passed: shallow/deep/gray alpha composites, complete silhouette, upright orientation and visible role-specific weapons/legs',rootIndependentReview='passed: parent inspected light and dark final 25-unit contacts',engineNotVerified=True)
    assert q['alphaRange']==[0,255] and q['clearBorder'] and q['substantialConnectedComponents']==1 and q['tinyDetachedPixels']==0
    a['validation']['visualReview']='passed';a['validation']['reviewedAt']=NOW;a['validation']['rootIndependentReview']='passed';a['validation']['backgrounds']=['ivory RGB 244,241,231','deep blue-gray RGB 31,42,47','gray RGB 127,127,127'];a['validation']['components']=q
    a['status']='art_complete_engine_not_verified';qa.append(q)
    gp=ROOT/a['generationRecord'];g=read(gp);g['validation']=q;write(gp,g)

all_checks=[]
for f,info in sorted(current.items()):
    p=ROOT/f;im=Image.open(p);a=np.asarray(im);al=a[:,:,3];bb=im.getbbox();margins=[bb[0],bb[1],im.width-bb[2],im.height-bb[3]]
    row=dict(file=f,sha256=sha(p),mode=im.mode,size=list(im.size),alphaRange=[int(al.min()),int(al.max())],margins=margins,transparentRgbIsZero=bool(np.all(a[al==0,:3]==0)))
    assert row['mode']=='RGBA' and row['alphaRange']==[0,255] and min(margins)>=12 and row['transparentRgbIsZero'];all_checks.append(row)

contacts=[]
for name in ['qa-light.jpg','qa-dark.jpg']:
    p=OWN/name;im=Image.open(p);g=dict(schemaVersion=1,file=rel(p),sha256=sha(p),createdAt=NOW,route='local-derived',tool='Python/Pillow',actualModel=None,actualQuality=None,purpose='final design overview and alpha-composite acceptance evidence; not a native generated board or runtime asset',width=im.width,height=im.height,operation='25 final unit images fitted down into 5 by 5 contact grid; labeled with official unit IDs; no upscaling',derivedFrom=[dict(file=a['file'],sha256=a['sha256'],generationRecord=a['generationRecord']) for a in m['assets']])
    gp=p.with_suffix('.jpg.generation.json');write(gp,g);contacts.append(dict(file=rel(p),sha256=g['sha256'],generationRecord=rel(gp)))

# Every source-board hash and generation receipt is preserved before deleting image-only intermediates.
delete_files=list((OWN/'boards').glob('*.png'))+list((OWN/'boards').glob('*-qa.jpg'))+list(OWN.glob('*-inspection.jpg'))+[OWN/'qa-gray.jpg']
deletions=[]
for p in delete_files:
    if not p.exists():continue
    resolved=p.resolve();assert resolved.is_relative_to(OWN.resolve()) and resolved.is_file()
    deletions.append(dict(file=rel(p),sha256=sha(p),sizeBytes=p.stat().st_size,reason='Final independent unit/layer PNGs and provenance verified; user retention policy removes rejected images, slicing-only source boards and temporary inspection renders. No image backup retained.',deletedAt=NOW))

source_paths={d['file'] for d in deletions if d['file'].endswith('.png')}
for gp in REC.glob('*.generation.json'):
    g=read(gp)
    if g.get('file') in source_paths:
        g['sourceImageRetained']=False;g['removedAt']=NOW;g['removalReason']='Final cropped body/part PNGs or accepted replacement layers exported and verified; source-board image removed under user retention policy.'
    for reference in g.get('references',[]):
        rp=Path(reference['file'])
        if rp.is_relative_to(ROOT) and rel(rp) in source_paths:
            reference['sourceImageRetained']=False;reference['generationRecord']=rel(REC/(rp.stem+'.generation.json'))
    write(gp,g)
for gp in list((OWN/'bodies').glob('*.generation.json'))+list((OWN/'parts').glob('*.generation.json')):
    g=read(gp)
    for src in g.get('derivedFrom',[]):
        if src.get('file') in source_paths:src['sourceImageRetained']=False;src['retentionNote']='Historical native-source path/hash; source board removed after verified independent export.'
    write(gp,g)

m.update(status='art_complete_engine_not_verified',finalizedAt=NOW,sourceImagesRetained=False,finalContacts=contacts,validationRecord=rel(REC/'final-validation.json'),retentionRecord=rel(REC/'retention-cleanup.json'))
write(OWN/'manifest.json',m);write(REC/'manifest.json',m)
write(REC/'final-validation.json',dict(schemaVersion=1,validatedAt=NOW,result='passed_art_validation',scopeCount=25,uniqueCurrentPngCount=len(current),ownCurrentPngCount=sum(f.startswith('units/serpulo-ground-naval/') for f in current),rootSuppliedBodyCount=5,sharedPartCount=30,unitChecks=qa,imageChecks=all_checks,contacts=contacts,openArtIssues=[],engineNotVerified=True,limitation='Actual engine packing, pixels-per-world-unit, texture-axis adaptation, team masks and motion/recoil are integration tasks outside this static art verification.'))
write(REC/'retention-cleanup.json',dict(schemaVersion=1,recordedAt=NOW,deletedImages=deletions,retainedCurrentImages=[dict(file=f,sha256=sha(ROOT/f)) for f in sorted(current)]+contacts,sourceTextAndHashesRetained=True,scope='Only this worker directory. No other worker image or Git state changed.'))
for p in delete_files:
    if p.exists():p.unlink()
print(json.dumps(dict(status=m['status'],units=25,currentPngs=len(current),ownPngs=75,externalBodies=5,sharedParts=30,deletedImages=len(deletions),manifest=rel(REC/'manifest.json'),contacts=contacts),ensure_ascii=False))
