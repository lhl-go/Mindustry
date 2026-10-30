from build import *

now=datetime.now(timezone.utc).isoformat()
m=rd(B/'manifest.json');q=rd(B/'qa/report.json')
assert len(m['assets'])==290 and not q['issues']
assert len({a['sourcePath'] for a in m['assets']})==290
allrows=m['assets']+m['additionalAtlasRegions']+m['generatedAtlasRegions']
checks=[]
for a in allrows:
 p=R/a['file'];im=Image.open(p).convert('RGBA');arr=np.array(im)
 assert sha(p)==a['sha256'] and im.getbbox(),a['id']
 assert (R/a['generationRecord']).exists(),a['id']
 if a.get('role','').endswith('_mask'):
  assert np.all(arr[arr[:,:,3]>0,:3]==255),a['id']
 if a.get('nativeFile'):
  a['nativeSha256']=sha(R/a['nativeFile'])
  assert a.get('nativeGenerationRecord') and (R/a['nativeGenerationRecord']).exists()
 a['status']='accepted_art_engine_not_verified';a['engineNotVerified']=True
 a['engineFile']=a['file'];a['engineSha256']=a['sha256']
 checks.append(dict(id=a['id'],file=a['file'],sha256=a['sha256'],size=list(im.size)))

unitSource='records/reference-unit-sources/UnitTypes.java'
shaderRules={
 'conquer-glow':dict(function='RegionPart.draw',tint='Color.red',blending='additive',progress='default warmup',layer=-1,outline=False,sourceLines=[3142,3147]),
 'conquer-weapon-glow':dict(function='RegionPart.draw',tint='Color.red',blending='additive',outline=False,mirror=False,sourceLines=[3007,3011]),
 'conquer-weapon-sinks-heat':dict(function='RegionPart.draw',tint='RGBA(1,0,0,0) -> RGBA(1,0,0,0.5)',blending='additive',progress='warmup',mirror=True,outline=False,moveX=4.25,moveY=-3.75,x=8,y=-8.5,sourceLines=[3032,3042])}
for a in m['assets']:
 if a['id'] in shaderRules:
  rule={**shaderRules[a['id']], 'sourceFile':unitSource,'sourceSha256':sha(R/unitSource),'geometry':'Independent mask aligned to its new body/weapon/sinks base; all original runtime transforms retained.'}
  a['runtimeShader']=rule;p=R/a['generationRecord'];j=rd(p);j['runtime']=rule;wr(p,j)

contacts=m['contacts']+[rel(B/'qa/additional-dark.png'),rel(B/'qa/additional-light.png'),rel(B/'qa/treads-frames.png')]
m['contacts']=contacts
q.update(status='passed_art_and_source_geometry_engine_not_verified',checkedAt=now,visualReview=dict(status='passed',reviewer='units_air_erekir',method='Actually viewed all 14 atlas/mask dark-light contacts plus 2 extra-component contacts and the 144-frame tread sheet.',criteria=['complete silhouettes and transparent edges','independent components have complete joint/pivot bases','neutral masks remain inside new shapes','official canvas and center preserved','all 144 runtime strips nonempty and in frame order'],contacts=[dict(file=f,sha256=sha(R/f)) for f in contacts],caveat='Contacts magnify small original-resolution atlas texels for inspection; they do not imply native HD resolution or in-engine verification.'),neutralMaskRgbVerified=True,extraAtlasCount=2,generatedTreadCount=144,uniqueGeneratedTreadHashes=len({a['sha256'] for a in m['generatedAtlasRegions']}),extraAndGeneratedChecks=checks[290:])
wr(B/'qa/report.json',q)

# Retain text provenance and exact original geometry, but do not retry an already
# blocked filesystem cleanup through another route. The coordinator can omit
# these intermediate images from the delivered archive without deleting them.
exclude=sorted([rel(p) for p in (B/'reference').rglob('*.png')]+[rel(B/'source/unit-bases-joints.png'),rel(B/'source-part-inspection.png')])
ret=dict(status='local_cleanup_not_attempted_after_prior_policy_rejection',sourceImageRetained=True,excludeFromDeliveryArchive=True,previousRejectionRecord='full-game/items-fx/retention-cleanup.json',reason='A prior scoped removal of consumed source/intermediate PNGs was rejected by automatic approval review (blocked by policy), with no further reason. No alternate local deletion route is used.',localFilesDeleted=False,paths=exclude,assets=[dict(file=f,sha256=sha(R/f),sourceImageRetained=True,excludeFromDeliveryArchive=True,reason='Consumed generation/reference/inspection image; current final exports and textual provenance are complete.') for f in exclude],createdAt=now)
wr(B/'retention-cleanup.json',ret)
for p in [B/'incite.png.fetch.json',B/'merui-weapon.png.fetch.json']:
 if p.exists():
  j=rd(p)
  if 'content' in j:
   j.pop('content');j['binaryPayloadRetained']=False;j['payloadDisposition']='Consumed reference image data omitted; original path, Git blob, dimensions and SHA retained in source-inventory.json.';wr(p,j)
src=B/'source/unit-bases-joints.png.generation.json';j=rd(src);j.update(sourceImageRetained=True,excludedFromDeliveryArchive=True,retentionRecord=rel(B/'retention-cleanup.json'));wr(src,j)

audit=rd(B/'audit.json')
if not (B/'records/initial-input-audit.json').exists():wr(B/'records/initial-input-audit.json',audit)
bySource={a['sourcePath']:a for a in m['assets']}
for a in audit['assets']:
 final=bySource[a['sourcePath']];a.update(mapping=dict(file=final['engineFile'],sha256=final['engineSha256'],generationRecord=final['generationRecord'],nativeFile=final['nativeFile'],nativeSha256=final['nativeSha256'],role=final['role']),status='accepted_art_engine_not_verified',output=final['engineFile'])
audit.update(status='complete_art_atlas_exports_engine_not_verified',mapped=290,unmapped=[],mappingConflictsResolved=m['mappingConflictsResolved'],manifest=rel(B/'manifest.json'),qaReport=rel(B/'qa/report.json'),checkedAt=now)
wr(B/'audit.json',audit)
si=rd(B/'source-inventory.json')
for a in si['assets']:
 final=bySource[a['sourcePath']];a.update(status='accepted_art_engine_not_verified',output=final['engineFile'],sourceImageRetained=True,referenceExcludedFromDeliveryArchive=True)
si['status']='all_290_original_paths_verified_and_exported';wr(B/'source-inventory.json',si)
m.update(status='complete_art_atlas_exports_engine_not_verified',frozenAt=now,qaReport=rel(B/'qa/report.json'),retentionCleanup=rel(B/'retention-cleanup.json'),readme=rel(B/'README.md'),runtimeVerified=False,officialSourceCanvasCount=290,additionalAtlasCount=2,generatedTreadFrameCount=144)
wr(B/'manifest.json',m)
wr(B/'freeze-receipt.json',dict(status=m['status'],frozenAt=now,manifest=rel(B/'manifest.json'),manifestSha256=sha(B/'manifest.json'),qaReport=rel(B/'qa/report.json'),qaSha256=sha(B/'qa/report.json'),counts=dict(sourcePaths=290,masks=87,newPaintedComponents=6,additionalWeaponBases=2,generatedTreadFrames=144),engineNotVerified=True,localCleanupDeleted=False,archiveExcludedImageCount=len(exclude)))
print(json.dumps(rd(B/'freeze-receipt.json')))
