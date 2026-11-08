"""Identify consumed local images only after accepted final exports are complete."""
from export_common import *
def main():
 m=read(HERE/'manifest.json');assert m['status']=='art_export_complete_runtime_unverified'
 keep=set()
 for a in m['assets']+m['sourceMappings']+m['integrationGeometryInputs']:
  for k in ['file','nativeFile']:
   if a.get(k):keep.add(a[k])
  if a.get('file')and a.get('sha256'):assert sha(ROOT/a['file'])==a['sha256']
 candidates=list((HERE/'boards').glob('*.png'))+list((HERE/'reference-sprites').rglob('*.png'))+list((HERE/'records').glob('*.png'))
 candidates+=list((HERE/'qa').glob('root-working-*.png'))+list((HERE/'qa').glob('core-thruster-audit-contact*.jpg'))
 candidates+=[HERE/'qa'/n for n in ['root-direction-audit-1.png','root-direction-audit-2.png','root-direction-audit-3.png','root-direction-audit-4.png','root-direction-audit-assemblies.png']]
 rows=[]
 for p in sorted(set(candidates)):
  if not p.exists()or rel(p)in keep:continue
  assert p.resolve().is_relative_to(HERE.resolve())and not p.is_symlink()
  rows.append({'file':rel(p),'absolutePath':str(p.resolve()),'sha256':sha(p),'excludeFromDeliveryArchive':True,'localFilePresent':True,'reason':'Consumed source board/reference or superseded inspection image; accepted final art, necessary geometry and textual provenance retained.'})
 write(HERE/'retention-cleanup-plan.json',{'createdAt':datetime.now(timezone.utc).isoformat(),'status':'verified_candidates_not_yet_removed','protectedFiles':len(keep),'files':rows})
 print(json.dumps({'candidates':len(rows),'protectedFiles':len(keep),'bytes':sum(Path(a['absolutePath']).stat().st_size for a in rows)}))
if __name__=='__main__':main()
