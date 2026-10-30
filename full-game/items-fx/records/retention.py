from build import *
paths=sorted((BASE/'source').glob('*.png'))+[BASE/'contact.png',BASE/'records/rubble-check.png'];rows=[]
for p in paths:
 if p.exists():rows.append(dict(file=p.relative_to(ROOT).as_posix(),sha256=sha(p),sourceImageRetained=True,excludeFromDeliveryArchive=True,reason='Consumed image-generation source sheet or superseded internal contact; all final assets and complete textual provenance retained.'))
write(BASE/'retention-cleanup.json',dict(status='local_deletion_rejected_by_automatic_approval',attemptedAt=datetime.now(timezone.utc).isoformat(),imageCount=len(rows),files=rows,receipt='exec_command CreateProcess rejected: blocked by policy. No more specific reason disclosed.',action='Non-recursive PowerShell Remove-Item -LiteralPath of verified files inside full-game/items-fx only.',retryPolicy='Stopped; no alternate deletion route attempted.',deliveryPolicy='Coordinator must filter these exact paths from final archive; local copies remain and are not represented as deleted.'))
m=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'));m['retentionCleanup']='full-game/items-fx/retention-cleanup.json';write(BASE/'manifest.json',m)
print(json.dumps({'retainedExcluded':len(rows)}))
