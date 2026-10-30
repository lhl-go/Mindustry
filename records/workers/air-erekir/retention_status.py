from pipeline import *
plan=json.loads((HERE/'cleanup-plan.json').read_text(encoding='utf-8-sig'));pending={x['file'] for x in plan['files']}
reason='Automatic approval rejected Remove-Item cleanup command with blocked by policy; no detailed reason returned. No files were deleted. No retry through an alternative route.'
def restore(obj):
 if isinstance(obj,dict):
  f=obj.get('file') or obj.get('path')
  if isinstance(f,str):
   normalized=f.replace('\\','/');prefix=ROOT.as_posix()+'/'
   if normalized.startswith(prefix):normalized=normalized[len(prefix):]
   if normalized in pending:
    assert (ROOT/normalized).is_file(),normalized
    obj['sourceImageRetained']=True;obj['deletionPending']=True;obj['retentionReason']=reason;obj.pop('sourceDeletionReason',None)
    if 'imageRetained' in obj:obj['imageRetained']=True
    if obj.get('status')=='source_image_removed_after_final_export':obj['status']='intermediate_retained_cleanup_blocked'
    if isinstance(obj.get('evidence'),dict):obj['evidence']['sourceBytesPreserved']=True
  for v in list(obj.values()):restore(v)
 elif isinstance(obj,list):
  for v in obj:restore(v)
for folder in [ROOT/'units/air-erekir',HERE]:
 for p in folder.rglob('*.json'):
  try:obj=json.loads(p.read_text(encoding='utf-8-sig'))
  except Exception:continue
  restore(obj);write(p,obj)
plan.update(status='blocked_by_automatic_approval_no_deletion_executed',sourceImageRetained=True,deletionPending=True,actuallyDeletedImageCount=0,reason=reason,packagingAction='Root will exclude listed intermediate image files from delivery archive without deleting local files.',rejectionReceipt={'tool':'exec_command','operation':'PowerShell Remove-Item -LiteralPath of validated own-directory paths with SHA256 preconditions','error':'Rejected: blocked by policy','detail':'No more specific reason disclosed.'})
write(HERE/'cleanup-plan.json',plan);write(HERE/'retention-cleanup.json',plan)
m=json.loads((HERE/'manifest.json').read_text(encoding='utf-8'));m['retentionCleanup']='records/workers/air-erekir/retention-cleanup.json';m['manifestWriteOwnership']='root_after_2026-10-26_handoff';m['status']='ready_25_units_3_pending_coordinator_patch';m['cleanupStatus']='blocked_local_intermediates_retained_archive_filter_requested'
for a in m['assets']:
 if a['id'] in ['poly','elude','avert']:a['status']='pending_coordinator_patch'
write(HERE/'manifest.json',m)
print(json.dumps({'manifest':str(HERE/'manifest.json'),'localPendingImages':len(pending),'deleted':0,'imagesFrozen':True,'writeOwnership':'root'}))
