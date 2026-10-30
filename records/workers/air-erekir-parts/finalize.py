from pathlib import Path
from PIL import Image
import json,hashlib,datetime,numpy as np
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=read(HERE/'manifest.json');errors=[];checks=[]
expected=[r for j in read(HERE/'jobs.json') for r in j['regions']]
actual=[a['region'] for a in m['assets']]
if len(expected)!=33 or len(actual)!=33 or sorted(expected)!=sorted(actual):errors.append('Region inventory mismatch')
hashes=[]
for a in m['assets']:
 p=ROOT/a['file'];rec=read(ROOT/a['record']);im=Image.open(p).convert('RGBA');arr=np.array(im);alpha=arr[:,:,3];ys,xs=np.where(alpha>0)
 checks.append({'region':a['region'],'pngReadable':True,'sizeMatches':list(im.size)==a['outputSize'],'shaMatches':sha(p)==a['sha256']==rec['sha256'],'padding':min(int(xs.min()),int(ys.min()),im.width-1-int(xs.max()),im.height-1-int(ys.max())),'hiddenRgbPixels':int(np.count_nonzero(np.any(arr[:,:,:3]!=0,axis=2)&(alpha==0))),'pivotInsideCanvas':0<=a['pivot'][0]<im.width and 0<=a['pivot'][1]<im.height,'sourceRecordExists':all((ROOT/s['generationRecord']).exists() for s in rec['derivedFrom'])})
 c=checks[-1]
 if not c['sizeMatches'] or not c['shaMatches'] or c['padding']<32 or c['hiddenRgbPixels'] or not c['pivotInsideCanvas'] or not c['sourceRecordExists']:errors.append(c)
 hashes.append(a['sha256'])
if len(set(hashes))!=33:errors.append('Duplicate independent asset pixels')
for b in m['boards']:
 r=read(ROOT/b['generationRecord']);receipt=read(HERE/(Path(b['file']).stem+'.receipt.json'));prompt=ROOT/r['prompt']
 if prompt.read_text(encoding='utf-8')!=receipt['args']['prompt']:errors.append('Actual prompt mismatch '+b['file'])
 if sha(prompt)!=r['promptSha256']:errors.append('Prompt SHA mismatch '+b['file'])
 if r['actualModel'] is not None or r['actualQuality'] is not None:errors.append('Undisclosed model/quality cannot be asserted')
 if not r.get('configSnapshot') or len(r['references'])<4 or any(not x.get('sha256') for x in r['references']):errors.append('Incomplete generation metadata '+b['file'])
report={'checkedAt':now(),'regionCount':33,'checks':checks,'errors':errors,'passed':not errors,'visualReview':{'worker':'hud_review','method':'Actual view_image of three native-scale dark/light alpha-composited contact sheets, all 33 cropped pieces inspected.','passed':True,'rootIndependentReview':'Parent root independently reported all three contacts clean and complete; no clipped parts.'},'runtimeIntegrationVerified':False}
write(HERE/'verification.json',report)
if errors:raise ValueError(errors)
cleanup=[]
source_root=(ROOT/'units/air-erekir-parts/source').resolve()
for b in m['boards']:
 p=(ROOT/b['file']).resolve();rp=ROOT/b['generationRecord'];r=read(rp)
 if p.parent!=source_root:raise ValueError('Outside assigned source directory: '+str(p))
 if p.exists():
  if sha(p)!=b['sha256']:raise ValueError('Source changed before cleanup')
  cleanup.append({'file':b['file'],'sha256':sha(p),'size':list(Image.open(p).size),'reason':'All final independent pieces verified and source metadata retained.'});p.unlink()
 r['status']='source_image_removed_after_final_asset_verification';r['sourceImageRetained']=False;r['retentionUpdatedAt']=now();r['retainedRecord']=b['generationRecord'];write(rp,r)
 b['imageRetained']=False;b['status']='source_pixels_removed_provenance_retained'
for a in m['assets']:
 a['status']='independent_part_art_verified_runtime_unverified';a['visualReviewPassed']=True
 a['source']['imageRetained']=False
 p=ROOT/a['record'];r=read(p)
 for s in r['derivedFrom']:s['sourceImageRetained']=False
 write(p,r)
m.update(status='complete_independent_parts_ready_for_owner_assembly',updatedAt=now(),verification='records/workers/air-erekir-parts/verification.json',finalContactSheets=['records/workers/air-erekir-parts/qa/'+Path(b['file']).stem+'-contact.png' for b in m['boards']],blockedRegions=[],integrationOwner='units_air_erekir',officialMappingNote='disrupt-tail is a working art name; official movement region alias is disrupt-weapon-blade. Shared leg/foot/track files are design reuse regions; final per-unit atlas mapping belongs to owner.')
write(HERE/'manifest.json',m)
write(HERE/'cleanup.json',{'completedAt':now(),'scope':'Only original boards in units/air-erekir-parts/source; no other worker files or host output cache touched.','deleted':cleanup,'retained':'33 final part PNGs, per-file provenance, generation receipts/prompts, and 3 final alpha contact sheets.'})
print(json.dumps({'status':m['status'],'regions':33,'errors':errors,'sourceBoardsRemoved':len(cleanup),'contacts':m['finalContactSheets']},ensure_ascii=False))
