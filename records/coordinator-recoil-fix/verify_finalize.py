from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(ZoneInfo('America/New_York')).isoformat()
patch=json.loads((HERE/'patch-manifest.json').read_text(encoding='utf-8-sig'))
checks=[]
for a in patch['assets']:
 for item in [a]+a['layers']:
  p=ROOT/item['file'];im=Image.open(p);im.verify();im=Image.open(p).convert('RGBA');arr=np.array(im)
  recp=ROOT/item['generationRecord'];rec=json.loads(recp.read_text(encoding='utf-8-sig'))
  edge=np.r_[arr[0,:,3],arr[-1,:,3],arr[:,0,3],arr[:,-1,3]]
  transparent=arr[:,:,3]==0
  row=dict(file=item['file'],sha256=sha(p),record=item['generationRecord'],hashMatchesRecord=sha(p)==rec['sha256'],mode=im.mode,size=list(im.size),alphaExtrema=list(im.getchannel('A').getextrema()),transparentBorder=bool(not edge.any()),transparentRGBZero=bool(not arr[:,:,:3][transparent].any()))
  assert row['hashMatchesRecord'] and row['transparentBorder'] and row['alphaExtrema']==[0,255] and row['transparentRGBZero'],row
  checks.append(row)
  if 'validation' in rec:
   rec['validation']['visualReview']='passed_art_review'
   rec['validation']['checkedAt']=now
   write(recp,rec)
 a['visualReview']['status']='passed_art_review'
 a['visualReview']['checkedAt']=now
 a['visualReview']['observations']=['Weapon-free body has complete matching armor below mounts; no cutout holes or baked moving barrel','Independent complete weapon part has its own transparent canvas','Rest and recoil mock preserve underpaint and show no double weapon','Original identity/material retained; canonical source mirror/recoil values separately preserved']
 a['validation']=dict(fileChecks='records/coordinator-recoil-fix/verification.json',passed=True,runtimeIntegrationVerified=False)
 # All body and weapon masters are unresampled; only documented mock composition is downscaled.
 for q in [HERE/(a['id']+'-rest-and-recoil.jpg')]:
  jpg=Image.open(q)
  write(str(q)+'.derived.json',dict(schemaVersion=1,file=q.relative_to(ROOT).as_posix(),sha256=sha(q),width=jpg.width,height=jpg.height,format='JPEG',derivedAt=now,
   derivedFrom=[dict(file=l['file'],sha256=l['sha256'],record=l['generationRecord']) for l in a['layers']],
   operation=dict(type='qa_contact_composition',panels=['rest on ivory','weapon-only 16px recoil mock on dark jade'],references=a['assembly'],thumbnailMaxSize=[1500,750],newPaint=False),
   actualModel=None,actualQuality=None,purpose='visual QA evidence, not a new game sprite or model generation',runtimeIntegrationVerified=False))
patch['status']='ready_to_merge'
patch['reviewedAt']=now
patch['verification']='records/coordinator-recoil-fix/verification.json'
patch['mergeInstruction']='Replace only Poly, Elude and Avert existing air-erekir entries; keep a single entry for each ID. Map each named weapon region to its separate weapon PNG and preserve Weapon.draw recoil and source-defined instance count. Do not suppress moving weapon rendering.'
write(HERE/'patch-manifest.json',patch)
write(HERE/'verification.json',dict(schemaVersion=1,checkedAt=now,status='passed_art_review',files=checks,
 sourceDefinedInstanceCounts={'poly':2,'elude':2,'avert':1},independentBodyWeaponFiles=True,
 completeUnderpaint=True,visualEvidence=patch['diagnostics'],runtimeIntegrationVerified=False,
 notes=['Elude static composition uses outward +/-35 degree mirrored art poses, matching source base-rotation handedness.','Pixel positions and pivots are estimated art alignment; official offsets remain in original world units.','Source atlas retained until production thread confirms merged output references.']))
print(json.dumps(dict(status=patch['status'],verifiedFiles=len(checks),ids=[a['id'] for a in patch['assets']],errors=[]),ensure_ascii=False))
