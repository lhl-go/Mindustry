from build import *

units=['stell','locus','precept','vanquish','conquer']
m=rd(B/'manifest.json');assets={a['id']:a for a in m['assets']};rows={a['region']:a for a in rd(B/'source-inventory.json')['assets']}
priorQa=rd(B/'qa/report.json');wr(B/'records/pre-motion-fix-qa.json',priorQa)
results=[]
for unit in units:
 a=assets[unit];t=assets[unit+'-treads'];reg=a.get('motionCorrection',{}).get('originalRegistration',a['registration']);originalFile=a.get('motionCorrection',{}).get('originalNativeFile',a['nativeFile'])
 source=Image.open(R/originalFile).convert('RGBA');trim=reg['sourceTrim'];sample=source.crop(trim);box=reg['officialAlphaBounds'];sample.thumbnail((box[2]-box[0],box[3]-box[1]),Image.Resampling.LANCZOS);sx=sample.width/(trim[2]-trim[0]);sy=sample.height/(trim[3]-trim[1]);px,py=reg['destinationTopLeft'];dx=round((a['size'][0]-t['size'][0])/2);dy=round((a['size'][1]-t['size'][1])/2)
 windows=[]
 for placement in t['registration']['placements']:
  for side in ['left','right']:
   x,y,w,h=placement[side];ix=max(1,round(w*.12));iy=max(1,round(h*.05))
   windows.append([x+dx+ix,y+dy+iy,x+dx+w-ix,y+dy+h-iy])
 arr=np.array(source);nativeWindows=[]
 for x0,y0,x1,y1 in windows:
  nx0=max(0,math.floor((x0-px)/sx+trim[0]));nx1=min(source.width,math.ceil((x1-px)/sx+trim[0]));ny0=max(0,math.floor((y0-py)/sy+trim[1]));ny1=min(source.height,math.ceil((y1-py)/sy+trim[1]));arr[ny0:ny1,nx0:nx1]=0;nativeWindows.append([nx0,ny0,nx1,ny1])
 native=Image.fromarray(arr);p=B/'revised-bodies'/f'{unit}-body.png';p.parent.mkdir(exist_ok=True);native.save(p)
 op=dict(type='authorized_motion_layer_separation',description='Clear only inner source-defined moving tread bands from the overlying body; retain outer rails, end armor and all other original painted pixels. Complete tread canvas fills the cleared areas below.',engineWindows=windows,nativeWindows=nativeWindows,sourceToEngineScale=[sx,sy],sourceTrim=trim,destinationTopLeft=[px,py],staticRailFractionPerSide=.12,staticEndFractionPerSide=.05,noNewPaintedPixels=True)
 wr(Path(str(p)+'.generation.json'),dict(file=rel(p),sha256=sha(p),width=native.width,height=native.height,format='PNG',mode='RGBA',derivedFrom=[srcinfo(R/originalFile)],operation=op,upsampled=False,actualModel=None,actualQuality=None,unverifiedReason='Authorized local layer separation from current final native art; no new model call.',engineNotVerified=True))
 crop=native.crop(trim).resize(sample.size,Image.Resampling.LANCZOS);out=Image.new('RGBA',tuple(a['size']));out.alpha_composite(crop,(px,py));oa=np.array(out)
 for x0,y0,x1,y1 in windows:oa[max(0,y0):min(out.height,y1),max(0,x0):min(out.width,x1)]=0
 oa[oa[:,:,3]==0,:3]=0;out=Image.fromarray(oa);ep=R/a['engineFile'];out.save(ep)
 wr(R/a['generationRecord'],dict(file=a['engineFile'],sha256=sha(ep),width=out.width,height=out.height,format='PNG',mode='RGBA',derivedFrom=[srcinfo(p)],operation=dict(type='original_canvas_export_after_layer_separation',sourceTrim=trim,sourceDimensions=list(native.size),destinationTopLeft=[px,py],scaledSize=list(sample.size),engineWindows=windows,registrationPreserved=True,edgeAntialiasRemovedInsideMotionWindows=True),officialSource=dict(path=a['sourcePath'],gitBlobSha1=a['sourceGitBlob'],sha256=a['sourceSha256']),upsampled=False,actualModel=None,actualQuality=None,unverifiedReason='Downsample of traced corrected native body; no new image generation.',engineNotVerified=True))
 a.update(file=rel(ep),sha256=sha(ep),engineSha256=sha(ep),nativeFile=rel(p),nativeSha256=sha(p),nativeGenerationRecord=rel(p)+'.generation.json',status='motion_correction_pending_visual',motionCorrection=dict(originalNativeFile=originalFile,originalRegistration=reg,**op));results.append(dict(id=unit,windows=windows,nativeWindows=nativeWindows))

exports={a['id']:a for a in m['assets']+m['additionalAtlasRegions']}
for unit in units:
 for suffix in ['-cell','-glow']:
  name=unit+suffix
  if name not in assets:continue
  a=assets[name];new=mask_export(name,rows[name],exports,rows);a.update(new,engineFile=new['file'],engineSha256=new['sha256'],nativeSha256=sha(R/new['nativeFile']),status='motion_correction_pending_visual')
  if a.get('runtimeShader'):
   rec=rd(R/a['generationRecord']);rec['runtime']=a['runtimeShader'];wr(R/a['generationRecord'],rec)
m['status']='tank_motion_layers_corrected_pending_final_qa';m['motionCorrection']=dict(sourceOrder='UnitType.java drawTank at 1513 precedes drawBody at 1546',bodyPixelSeparation=True,units=results);wr(B/'manifest.json',m)
print(json.dumps({'correctedBodies':len(results),'updatedMasks':6,'nativeFiles':[assets[u]['nativeFile'] for u in units]}))
