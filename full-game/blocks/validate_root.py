from export_common import *
from collections import Counter
import re
batch=HERE/'batches/root.json'
m=read(batch if batch.exists()else HERE/'batches/root-working.json');rows=m['sourceMappings'];errors=[];checks=[];by={a['region']:a for a in rows}
for a in rows:
 p=ROOT/a['file'];im=Image.open(p).convert('RGBA');row=ROWS[a['region']];op,orig=original(row);arr=np.asarray(im);o=np.asarray(orig)
 issue=[]
 if sha(p)!=a['sha256']:issue.append('hash')
 if sha(ROOT/a['nativeFile'])!=a['nativeSha256']:issue.append('native_hash')
 if im.size!=orig.size:issue.append('canvas')
 if not im.getchannel('A').getbbox()and orig.getchannel('A').getbbox():issue.append('unexpected_empty')
 if a['disposition']=='exact_upstream_technical_reuse'and sha(p)!=sha(op):issue.append('technical_bytes')
 if a['operation'].get('kind')in ['painted_material_with_exact_official_connection_and_phase_geometry','painted_material_with_original_layer_or_state_geometry','painted_material_on_original_liquid_window_frame']:
  if not np.array_equal(arr[:,:,3],o[:,:,3]):issue.append('original_connection_alpha')
 if a['disposition']=='new_body_aligned_technical_mask'and np.any(arr[:,:,:3][arr[:,:,3]>0]!=255):issue.append('nonneutral_tint_mask')
 if a['region'].endswith('-open'):
  if arr[im.height//2,im.width//2,3]!=0:issue.append('door_passage_blocked')
 checks.append({'region':a['region'],'file':a['file'],'sha256':sha(p),'issues':issue});errors.extend(a['region']+':'+s for s in issue)
motion=[]
for family in ['conveyor','titanium-conveyor','armored-conveyor']:
 for i in range(5):
  names=[f'{family}-{i}-{j}'for j in range(4)]
  if all(n in by for n in names):
   count=len({by[n]['sha256']for n in names});motion.append({'family':family,'connection':i,'uniqueFrames':count})
   if count!=4:errors.append(f'{family}-{i}:duplicate_animation_frame')
report={'checkedAt':datetime.now(timezone.utc).isoformat(),'sourceCount':len(rows),'completeExpected':len(rows)==367,'errors':errors,'checks':checks,'conveyorPhaseChecks':motion,'runtimeIntegrationVerified':False,'scope':'Exact source paths/canvases, native hashes, functional original connections, liquid windows, open-door passages and neutral masks; actual engine has not run.'}
write(HERE/'qa/root-validation.json',report);print(json.dumps({k:v for k,v in report.items()if k!='checks'}))
if errors:raise SystemExit(1)
