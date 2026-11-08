"""Record the completed human-visible static review after validate_industry.py."""
from export_common import *

m=read(HERE/'batches/hud_review.json');v=read(HERE/'qa/industry-validation.json')
assert len(m['sourceMappings'])==251 and not v['errors']
for a in m['sourceMappings']:
 assert sha(ROOT/a['file'])==a['sha256'] and sha(ROOT/a['nativeFile'])==a['nativeSha256']
 assert next(c['sha256'] for c in v['checks'] if c['region']==a['region'])==a['sha256']
for a in v['assemblyContacts']:assert sha(ROOT/a['file'])==a['sha256']

nativeGroups=['production-serpulo-01','production-processors-02','production-heat-03',
 'mining-bodies-01','power-static-01','power-reactors-02','moving-rotors-01']
viewed=[HERE/'qa'/(n+'-'+bg+'.jpg')for n in nativeGroups for bg in ['light','dark']]
viewed += [ROOT/p for p in m['contacts']]+[ROOT/a['file'] for a in v['assemblyContacts']]
viewed += [HERE/'qa/industry-diode-cleanup-preview.png']
review={'reviewedAt':datetime.now(timezone.utc).isoformat(),'status':'passed_static_art_review_runtime_unverified',
 'sourceCount':251,'actualVisualReview':'Every listed final image was opened with view_image and inspected after its last pixel change.',
 'images':[{'file':rel(p),'sha256':sha(p),'actualVisualReview':'pass'}for p in viewed],
 'validation':{'file':'full-game/blocks/qa/industry-validation.json','sha256':sha(HERE/'qa/industry-validation.json')},
 'observations':[
  'Native production, mining, power and moving-part boards retain jade, ivory and warm-gold style, readable silhouettes and clean exterior transparency on both backgrounds.',
  'All 251 compatibility regions were viewed on light/dark backgrounds; tiny/white regions are intentionally technical stencils at upstream dimensions, not missing paintings.',
  'Diode base no longer has an unrotatable north arrow. Its existing jade material patch is recorded; only diode-arrow carries the runtime direction.',
  'Pulverizer top is a four-corner support and small axle, not a full-diameter hub. Its 86.51% surviving rotor alpha and visible angle changes are checked.',
  'Other drill/extractor hub caps leave 54.06% to 77.94% rotor alpha visible. Steam uses two counter-rotating instances and a separate stationary cap.',
  'Weaves and 4/8 radial piston parts remain visible through original body windows. Four impact-reactor plasma regions are simultaneously additive, never mistaken for successive animation frames.',
  'Heat masks preserve original single-edge alpha and neutral RGB. Directional top1/top2 structures remain separate. Original liquid stencils and source window geometry are retained.',
  'Where original functional canvas extends beyond a native silhouette, existing liquid-source jade pixels provide a documented material patch. No procedural painting or new native detail is claimed.'
 ],'fixes':['Removed baked diode direction from compatibility base','Corrected pulverizer top occlusion','Replaced stretched transparent-padding edge streaks with a provenance-recorded existing jade material patch'],
 'sourceInformedMotionCases':len(v['motionChecks']),'runtimeIntegrationVerified':False,
 'limitations':['The actual Mindustry engine has not run. Inspection compositions are layer-order fixtures, not engine screenshots.','Procedural particles, dynamic liquids and hardware blending require subsequent runtime acceptance.'],
 'additionalSharedPartReview':'full-game/blocks/qa/detached-parts-review.json'}
write(HERE/'qa/industry-final-review.json',review)
for a in m['sourceMappings']:
 a['status']='art_export_complete_runtime_unverified'
 a['staticReview']='full-game/blocks/qa/industry-final-review.json'
 write(ROOT/a['record'],a)
m.update(status='art_export_complete_runtime_unverified',staticReviewPending=False,
 reviewedAt=review['reviewedAt'],errors=[],review={'file':'full-game/blocks/qa/industry-final-review.json','sha256':sha(HERE/'qa/industry-final-review.json')})
refs=[ROOT/'records/reference-dynamic-sources'/('core__src__mindustry__world__blocks__'+s+'.java') for s in ['power__PowerDiode','production__Drill','production__WallCrafter','production__BeamDrill','power__ImpactReactor']]
m['codeInputs'] += [{'file':rel(p),'sha256':sha(p)}for p in refs]
write(HERE/'batches/hud_review.json',m)
receipt={'frozenAt':datetime.now(timezone.utc).isoformat(),'status':m['status'],'sourceCount':251,
 'batch':{'file':'full-game/blocks/batches/hud_review.json','sha256':sha(HERE/'batches/hud_review.json')},
 'review':m['review'],'validation':review['validation'],'integrationGeometryInputCount':len(m['integrationGeometryInputs']),
 'runtimeIntegrationVerified':False}
write(HERE/'qa/industry-freeze-receipt.json',receipt)
print(json.dumps(receipt))
