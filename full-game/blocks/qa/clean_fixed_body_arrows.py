"""Authorized local removal of fixed directional glyphs; no new painted detail.

Only the explicit glyph mask changes. Existing surrounding RGB is harmonically
interpolated into that mask, preserving the source alpha and every other pixel.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from export_common import *
from PIL import ImageFilter

OUT=HERE/'masters-derived';OUT.mkdir(exist_ok=True)
MASKS={
 'surge-router':[(133,146),(163,125),(195,148),(196,168),(182,172),(164,157),(146,172),(132,166)],
 'overflow-duct':[(127,162),(153,139),(179,161),(180,182),(167,185),(153,172),(138,185),(126,180)],
 'underflow-duct':[(144,130),(170,109),(198,132),(198,152),(185,155),(170,141),(155,155),(143,150)],
 'liquid-overflow-gate':[(174,32),(194,65),(192,73),(183,75),(178,87),(168,82),(164,73),(153,71),(154,64)]
}

def clean(name,points):
 src,im=master(name);a=np.asarray(im).copy()
 mask=Image.new('L',im.size);ImageDraw.Draw(mask).polygon(points,fill=255)
 m=np.asarray(mask)>0
 ring=(np.asarray(mask.filter(ImageFilter.MaxFilter(7)))>0)&~m
 work=a[:,:,:3].astype(float);work[m]=np.median(work[ring],axis=0)
 for _ in range(1500):
  avg=(np.roll(work,1,0)+np.roll(work,-1,0)+np.roll(work,1,1)+np.roll(work,-1,1))*.25
  work[m]=avg[m]
 out=a.copy();out[m,:3]=np.clip(np.rint(work[m]),0,255).astype('uint8')
 p=OUT/(name+'.png');Image.fromarray(out).save(p)
 assert np.array_equal(a[:,:,3],out[:,:,3])and np.array_equal(a[~m],out[~m])
 rec={'file':rel(p),'sha256':sha(p),'nativeSize':list(im.size),'derivedFrom':[{'file':rel(src),'sha256':sha(src),'generationRecord':rel(src)+'.derived.json'}],
 'operation':{'type':'authorized_local_fixed_directional_glyph_cleanup','maskPolygon':points,'maskPixels':int(m.sum()),'method':'Harmonic RGB interpolation from existing adjacent source pixels, 1500 Jacobi iterations; no outside pixel or alpha changes','newPaintedDetail':False,'scale':1},
 'reason':'This fixed body must not encode a directional arrow; the separately rotating original top region supplies direction.',
 'runtimeIntegrationVerified':False,'actualModel':None,'actualQuality':None,
 'runtimeEvidence':'Legacy source path; no active block definition in the fixed v160.7 Blocks.java'if name=='liquid-overflow-gate'else'DuctRouter/StackRouter/OverflowDuct use fixed body plus independently rotating top region.'}
 write(Path(str(p)+'.derived.json'),rec);return rec

def reusable(name,source,operation):
 src=ROOT/source;im=Image.open(src).convert('RGBA')
 if operation.get('rotationDegrees'):im=im.rotate(operation['rotationDegrees'],expand=True)
 p=OUT/(name+'.png');im.save(p)
 rec={'file':rel(p),'sha256':sha(p),'nativeSize':list(im.size),'derivedFrom':[{'file':rel(src),'sha256':sha(src),'generationRecord':rel(src)+'.derived.json'}],
 'operation':operation,'actualModel':None,'actualQuality':None,'runtimeIntegrationVerified':False,
 'reason':'Thruster.java is a decorative sandbox Wall: fixed base and independently rotating top, with no thrust/motion simulation.'}
 write(Path(str(p)+'.derived.json'),rec);return rec

def main():
 rows=[clean(n,p)for n,p in MASKS.items()]
 rows.append(reusable('thruster-base','full-game/units/parts/mech-base-heavy.png',{'type':'existing_native_stationary_pedestal_reuse','scale':1,'newPaintedDetail':False}))
 rows.append(reusable('thruster-top','full-game/blocks/masters/thruster.png',{'type':'existing_native_thruster_as_single_rotating_assembly','rotationDegrees':-90,'scale':1,'newPaintedDetail':False}))
 contact(rows_to_contact(rows),'root-direction-audit-cleaned')
 write(HERE/'qa/root-direction-audit-derived.json',{'assets':rows,'nativeFileCount':len(rows),'requiresCompatibilityIntegration':True,'runtimeIntegrationVerified':False})
 print(json.dumps({'derivedAssets':len(rows),'files':[r['file']for r in rows]}))

def rows_to_contact(rows):return[dict(a,region=Path(a['file']).stem)for a in rows]
if __name__=='__main__':main()
