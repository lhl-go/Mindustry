"""Read-only directional assembly audit; creates inspection evidence, no art edits."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from export_common import *

b=read(HERE/'batches/root.json');by={a['region']:a for a in b['sourceMappings']}
names=['surge-router','overflow-duct','underflow-duct','liquid-overflow-gate','duct-router','thruster']
rows=[];canvas=Image.new('RGB',(1080,len(names)*190),(28,44,43));d=ImageDraw.Draw(canvas)
for i,n in enumerate(names):
 base=Image.open(ROOT/by[n]['file']).convert('RGBA');top=Image.open(ROOT/by[n+'-top']['file']).convert('RGBA');size=(max(base.width,top.width),max(base.height,top.height))
 for rot in range(4):
  out=Image.new('RGBA',size);out.alpha_composite(base,((size[0]-base.width)//2,(size[1]-base.height)//2))
  t=top.rotate(rot*90,expand=True);out.alpha_composite(t,((size[0]-t.width)//2,(size[1]-t.height)//2));out=ImageOps.contain(out,(165,165),Image.Resampling.NEAREST)
  canvas.paste(out,(rot*270+80,i*190),out);d.text((rot*270+8,i*190+167),n+' rotation '+str(rot),fill=(240,240,220))
 for key in [n,n+'-top']:rows.append({'region':key,'file':by[key]['file'],'sha256':sha(ROOT/by[key]['file'])})
canvas.save(HERE/'qa/root-direction-audit-final-assemblies.png')
contact([by[n]for n in ['plastanium-conveyor','plastanium-conveyor-0','plastanium-conveyor-1','plastanium-conveyor-2','surge-conveyor','surge-conveyor-0','surge-conveyor-1','surge-conveyor-2','core-acropolis-thruster1','core-acropolis-thruster2','core-nucleus-thruster1','core-nucleus-thruster2','mass-driver-base','mass-driver']],'root-direction-audit-final-parts')
checks=[]
for n in ['surge-router','overflow-duct','underflow-duct','liquid-overflow-gate']:
 a=by[n];p=HERE/'masters-derived'/(n+'.png');r=read(Path(str(p)+'.derived.json'));src=ROOT/r['derivedFrom'][0]['file']
 before=np.asarray(Image.open(src));after=np.asarray(Image.open(p));mask=Image.new('L',Image.open(p).size);ImageDraw.Draw(mask).polygon([tuple(v)for v in r['operation']['maskPolygon']],fill=255);m=np.asarray(mask)>0
 assert a['nativeFile']==rel(p)and a['nativeSha256']==sha(p)
 assert np.array_equal(before[:,:,3],after[:,:,3])and np.array_equal(before[~m],after[~m])
 checks.append({'region':n,'fixedArrowRemoved':True,'alphaUnchanged':True,'allPixelsOutsideRemovalMaskUnchanged':True,'derivedNativeUsedByCompatibility':True})
for n in ['plastanium-conveyor','surge-conveyor']:
 for a in [by[n]]+[by[n+'-'+str(i)]for i in range(3)]:
  assert a['operation']['nativeMaterialRotationBeforePlacement']==-90
  checks.append({'region':a['region'],'nativeQuarterTurnBeforeExport':-90,'runtimeRule':'StackConveyor rotation zero is east; runtime still supplies normal quarter turns.'})
for a in b['sourceMappings']:
 if a['region'].startswith(('core-nucleus-thruster','core-acropolis-thruster')):
  assert a['operation']['localHorizontalMirror'] is True
  checks.append({'region':a['region'],'largeNativeNozzlesMirroredEast':True})
assert by['thruster']['nativeFile'].endswith('/thruster-base.png')and by['thruster-top']['nativeFile'].endswith('/thruster-top.png')
for n in ['underflow-duct','liquid-overflow-gate']:
 base=Image.open(ROOT/by[n]['file']).convert('RGBA');top=Image.open(ROOT/by[n+'-top']['file']).convert('RGBA')
 bb=base.getchannel('A').getbbox();tb=top.getchannel('A').getbbox()
 assert base.size==top.size and tb[0]>=bb[0]and tb[1]>=bb[1]and tb[2]<=bb[2]and tb[3]<=bb[3]
 checks.append({'region':n+'-top','indicatorBounds':tb,'newBodyBounds':bb,'originalCanvasAndPivotPreserved':True,'indicatorContainedByNewBodyBounds':True,'originalAlphaShapeRelocatedLocally':True})
source=[]
for filename in ['distribution__StackConveyor','distribution__DuctRouter','distribution__StackRouter','distribution__OverflowDuct','defense__Thruster','storage__CoreBlock','distribution__MassDriver']:
 p=ROOT/'records/reference-dynamic-sources'/('core__src__mindustry__world__blocks__'+filename+'.java');source.append({'file':rel(p),'sha256':sha(p)})
report={'checkedAt':datetime.now(timezone.utc).isoformat(),'status':'static_checks_passed_visual_review_pending','sourceBatch':{'file':rel(HERE/'batches/root.json'),'sourceCount':len(by),'artContentDigest':hashlib.sha256(json.dumps(sorted((a['file'],a['sha256'])for a in b['sourceMappings']),separators=(',',':')).encode()).hexdigest(),'digestDefinition':'SHA256 of sorted JSON pairs [file,sha256] for all exported root art; metadata status changes do not invalidate this audit.'},'checks':checks,'assemblySources':rows,'sourceCodeEvidence':source,
 'contactSheets':[{'file':rel(p),'sha256':sha(p)}for p in [HERE/'qa/root-direction-audit-final-assemblies.png',HERE/'qa/root-direction-audit-final-parts-01.png']],
 'findingsResolved':['Stack conveyor source axis normalized north-to-east before source-canvas mapping.','Four fixed body arrows removed from local derivative artwork, leaving direction to top layers.','Decorative thruster uses separate stationary pedestal and one rotating assembly.','Large core native nozzles mirrored east before original corner and runtime quarter-turn rules.'],
 'interpretationCorrections':['Duct-router central mark is a three-branch junction symbol, not a one-way arrow; retained.','Mass-driver north rectangular channel is the muzzle; south round feature is the rear pivot. No 180-degree turn was required.'],
 'limits':['Static assembly simulation only; Mindustry engine was not executed.','liquid-overflow-gate is an orphan legacy source pair with no active v160.7 Blocks.java definition. Structural base/top separation is retained, without claiming an active renderer.','Thruster extends Wall, is sandboxOnly, and has no thrust behavior.'],'runtimeIntegrationVerified':False}
write(HERE/'qa/root-direction-audit.json',report);print(json.dumps({'status':report['status'],'checks':len(checks)}))
