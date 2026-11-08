from build import *

now=datetime.now(timezone.utc).isoformat();m=rd(B/'manifest.json');q=rd(B/'qa/report.json');prior=rd(B/'records/pre-motion-fix-qa.json');motion=rd(B/'qa/tank-motion.json');connect=rd(B/'qa/conquer-alpha-connectivity.json');ret=rd(B/'retention-cleanup.json')
assert not q['issues'] and connect['bodyAndFrontTreadsConnected']
previous={a['id']:a['sha256'] for a in prior['checks']};changed=[a['id'] for a in q['checks'] if previous.get(a['id'])!=a['sha256']];assert len(changed)==11,changed
for a in m['assets']+m['additionalAtlasRegions']+m['generatedAtlasRegions']:
 assert sha(R/a['file'])==a['sha256'],a['id']
 if a.get('nativeFile'):assert sha(R/a['nativeFile'])==a['nativeSha256'],a['id']
 if a.get('role','').endswith('_mask'):
  p=np.array(Image.open(R/a['file']).convert('RGBA'));assert np.all(p[p[:,:,3]>0,:3]==255),a['id']
 a['status']='accepted_art_engine_not_verified'

extraContacts=[rel(B/'qa'/f) for f in ['additional-dark.png','additional-light.png','treads-frames.png','tank-revision-dark.png','tank-revision-light.png','tank-motion-dark.png','tank-motion-light.png']]
m['contacts']=q['contacts']+extraContacts
motion.update(status='passed_static_simulation_and_visual_engine_not_verified',checkedAt=now,visualReview='Both dark/light contact sheets actually inspected by producer and root; visible frame differences, preserved static rails and armor. Conquer has one connected main component at alpha thresholds 16/128/245 across frames 0/9/17.',connectivityReport=rel(B/'qa/conquer-alpha-connectivity.json'));wr(B/'qa/tank-motion.json',motion)
q.update(status='passed_art_source_geometry_and_static_motion_engine_not_verified',checkedAt=now,neutralMaskRgbVerified=True,generatedTreadCount=144,extraAtlasCount=2,uniqueGeneratedTreadHashes=len({a['sha256'] for a in m['generatedAtlasRegions']}),visualReview=dict(status='passed',changedAssetsActuallyReviewed=changed,changedAssetContactFiles=[rel(B/'qa/tank-revision-dark.png'),rel(B/'qa/tank-revision-light.png')],unchangedAssetsReusedByHash=len(q['checks'])-len(changed),previousReviewRecord=rel(B/'records/pre-motion-fix-qa.json'),method='Reused previously accepted visual checks for 279 identical asset hashes; actually viewed all 11 revised body/mask assets on dark/light contacts and both tank motion sheets. Refreshed full atlas contacts show current images.',currentContacts=[dict(file=f,sha256=sha(R/f)) for f in m['contacts']]),motionDrawOrderReport=rel(B/'qa/tank-motion.json'),motionDrawOrderReportSha256=sha(B/'qa/tank-motion.json'),conquerConnectivityReport=rel(B/'qa/conquer-alpha-connectivity.json'),conquerConnectivitySha256=sha(B/'qa/conquer-alpha-connectivity.json'),engineNotVerified=True)
wr(B/'qa/report.json',q)
m.update(status='complete_art_atlas_exports_engine_not_verified',frozenAt=now,activeIssue=None,staticDrawOrderSimulationVerified=True,motionQa=rel(B/'qa/tank-motion.json'),motionRevision=dict(revisedNativeBodies=5,revisedSourceExports=11,unmodifiedSourceExports=279,minimumExposedTreadFraction=min(z['uncoveredFraction'] for c in motion['checks'] for z in c['exposedMotionRectangles']),maximumExposedTreadFraction=max(z['uncoveredFraction'] for c in motion['checks'] for z in c['exposedMotionRectangles']),visibleFrameDifferenceRange=[min(c['visibleChangedPixels'] for c in motion['checks']),max(c['visibleChangedPixels'] for c in motion['checks'])]),runtimeVerified=False,engineNotVerified=True)
wr(B/'manifest.json',m)
audit=rd(B/'audit.json');bySource={a['sourcePath']:a for a in m['assets']}
for a in audit['assets']:
 en=bySource[a['sourcePath']];a['mapping'].update(file=en['file'],sha256=en['sha256'],nativeFile=en['nativeFile'],nativeSha256=en['nativeSha256'],generationRecord=en['generationRecord'],role=en['role']);a['status']='accepted_art_engine_not_verified'
audit.update(status=m['status'],checkedAt=now,mapped=290,unmapped=[],motionQa=rel(B/'qa/tank-motion.json'));wr(B/'audit.json',audit)
readme=B/'README.md';s=readme.read_text(encoding='utf-8');s=s.replace('17 张实际目检联系表','21 张验收联系表');s+='\n\n坦克运动层修订：五种坦克身体已从当前正式原生图中分离对应运动带，保留静态轮架、端部装甲和全部其他绘画像素；新增 5 张 `revised-bodies/` 原生分层派生图，原始画布锚点不变。同步更新 5 张 cell 与 conquer-glow 遮罩。按官方 treads 先画、body 后画的顺序离线合成后，运动矩形可见面积为 68.67%—93.39%，第 0/9 帧可见变化为 1221—9365 像素。Conquer 前履带与身体在 alpha 16/128/245 阈值下均为一个主体连通域。报告见 `qa/tank-motion.json` 与 `qa/conquer-alpha-connectivity.json`。此验证是源码绘制顺序的离线像素模拟，游戏实机验证仍未执行。\n';readme.write_text(s,encoding='utf-8')
wr(B/'freeze-receipt.json',dict(status=m['status'],frozenAt=now,revision='tank_motion_occlusion_corrected',manifest=rel(B/'manifest.json'),manifestSha256=sha(B/'manifest.json'),qaReport=rel(B/'qa/report.json'),qaSha256=sha(B/'qa/report.json'),motionQa=rel(B/'qa/tank-motion.json'),motionQaSha256=sha(B/'qa/tank-motion.json'),counts=dict(sourcePaths=290,masks=87,newPaintedComponents=6,revisedNativeBodies=5,additionalWeaponBases=2,generatedTreadFrames=144),staticDrawOrderSimulationVerified=True,engineNotVerified=True,localCleanupDeleted=ret.get('localFilesDeleted',False),localCleanupRecord=ret.get('completionRecord'),archiveExcludedImageCount=len(ret.get('paths',[]))))
print(json.dumps(rd(B/'freeze-receipt.json')))
