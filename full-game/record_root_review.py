"""Record the coordinator's direct visual inspection of final contact sheets."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent.parent;HERE=ROOT/'full-game'
paths=[
 ('terrain/qa/23-planet-icons-alpha.png','Planet identity, transparent perimeter on light/dark; no additional defect observed.'),
 ('terrain/qa/26-base-icons-shadows.png','Connection-dependent metal tiles and body-derived shadow alpha remain distinct technical layers.'),
 ('terrain/qa/27-skybox-space.png','Six projected sky faces and repeatable space texture; native projection and compatibility upscale are documented.'),
 ('units/qa/additional-dark.png','Six distinct native bases/joints and two independent weapon-base exports have clean silhouettes.'),
 ('units/qa/treads-frames.png','All eight 18-frame tread-strip groups present; one-pixel-wide runtime generator output is not misrepresented as new painting.'),
 ('units/qa/masks-02-dark.png','Cell, heat and glow overlays follow body/weapon surfaces; corrected conquer weapon/sink masks now use the corresponding component.'),
 ('units/qa/atlas-01-dark.png','Final corrected unit source exports include paired tank tread geometry.'),
 ('units/qa/masks-01-dark.png','Team-color and glow layers checked against corrected body placement; source canvas dimensions retained.'),
 ('units/qa/tank-motion-dark.png','Five tank bodies leave moving tread windows visible in the upstream tread-before-body drawing order; frame 0/9 differ visibly.'),
 ('units/qa/tank-motion-light.png','Light-background simulation confirms static armor is retained and exposed moving tracks remain attached; Conquer alpha connectivity is separately verified.')]
rows=[]
for rel,note in paths:
 p=HERE/rel
 rows.append({'file':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'reviewedDirectly':True,'result':'no_additional_static_visual_defect_observed','note':note})
result={'recordedAt':datetime.now(timezone.utc).isoformat(),'reviewer':'root coordinator','status':'selected_final_contacts_reviewed','sheets':rows,'scope':'Independent static visual spot checks in addition to each domain owner\'s full contact review and automated geometry/hash validation. The selected sheets are not a substitute for complete source-path coverage.','runtimeIntegrationVerified':False}
(HERE/'qa/coordinator-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'reviewedSheets':len(rows),'runtimeIntegrationVerified':False}))
