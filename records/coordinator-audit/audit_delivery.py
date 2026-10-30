"""Read-only audit of delivered artifacts; writes only this audit directory."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

BASE = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent

def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

hashes = {}
def digest(path):
    if path not in hashes:
        hashes[path] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes[path]

def exists(rel):
    return bool(rel) and (BASE / rel.split("?", 1)[0]).is_file()

def resolve_record(record, source_file, current_record):
    if exists(record):
        return record
    for parent in (Path(source_file).parent if source_file else Path(), Path(current_record).parent):
        candidate = str(parent / record).replace("\\", "/")
        if exists(candidate):
            return candidate
    return record

manifest_path = BASE / "exports/manifest.json"
ledger_path = BASE / "records/production-ledger.json"
manifest = read(manifest_path)
ledger = read(ledger_path)
inventory_units = read(BASE / "records/inventory-units.json")
inventory_ui = read(BASE / "records/inventory-ui.json")
issues = []
expected_units = {row["id"] for row in inventory_units["units"] if row.get("independentArtRequired")}
actual_units = manifest.get("units", [])
actual_ids = [row["id"] for row in actual_units]
missing_units = sorted(expected_units - set(actual_ids))
extra_units = sorted(set(actual_ids) - expected_units)
duplicate_ids = sorted({unit for unit in actual_ids if actual_ids.count(unit) > 1})

checked_assets = set()
checked_records = set()
historical_sources = []
def inspect_record(rel, depth=0):
    if not rel or rel in checked_records:
        return
    checked_records.add(rel)
    path = BASE / rel
    if not path.is_file():
        issues.append({"type":"missing_provenance_record", "file":rel})
        return
    row = read(path)
    refs = row.get("derivedFrom", [])
    if isinstance(refs, dict):
        refs = [refs]
    for source in refs:
        if not isinstance(source, dict):
            continue
        source_file = source.get("file") or source.get("path")
        record = source.get("generationRecord") or source.get("record")
        if source_file:
            source_path = BASE / source_file
            if source_path.is_file():
                if source.get("sha256") and digest(source_path) != source["sha256"]:
                    issues.append({"type":"source_hash_mismatch", "file":source_file, "record":rel})
            else:
                historical_sources.append({"file":source_file, "record":rel, "sha256":source.get("sha256")})
        if record and depth < 12:
            inspect_record(resolve_record(record, source_file, rel), depth+1)

def inspect_asset(row, kind):
    rel = row.get("file")
    if not rel or rel in checked_assets:
        return
    checked_assets.add(rel)
    path = BASE / rel
    if not path.is_file():
        issues.append({"type":"missing_asset", "kind":kind, "file":rel})
        return
    if row.get("sha256") and digest(path) != row["sha256"]:
        issues.append({"type":"asset_hash_mismatch", "kind":kind, "file":rel})
    record = row.get("record") or row.get("generationRecord")
    if not record:
        options = [rel+".generation.json", rel+".derived.json"]
        record = next((candidate for candidate in options if exists(candidate)), None)
    if not record:
        issues.append({"type":"unrecorded_asset", "kind":kind, "file":rel})
    else:
        inspect_record(record)
        if exists(record):
            data = read(BASE / record)
            if data.get("sha256") and data["sha256"] != digest(path):
                issues.append({"type":"provenance_asset_hash_mismatch", "file":rel, "record":record})

for unit in actual_units:
    inspect_asset(unit, "unit")
    for layer in unit.get("layers", []):
        inspect_asset({"file":layer} if isinstance(layer,str) else layer, "unit_layer")
for kit in manifest.get("kit", []):
    inspect_asset(kit, "ui_kit")
for concept in manifest.get("concepts", []):
    inspect_asset(concept, "concept")
if manifest.get("character"):
    inspect_asset(manifest["character"], "character")

ui = manifest.get("ui", [])
expected_ui = {row["id"] for key in ("screens","reusableDialogs","sharedComponents") for row in inventory_ui[key]}
ui_ids = [row["id"] for row in ui]
states = {(group["id"],state["index"]):state for group in ui for state in group.get("states",[])}
latest_checks = {}
report_summaries = []
for rel in manifest.get("renderReports", []):
    report = read(BASE / rel)
    changed_sources = []
    for source in report.get("sources", []):
        if not exists(source["file"]) or digest(BASE/source["file"]) != source["sha256"]:
            changed_sources.append(source["file"])
    report_summaries.append({"file":rel,"createdAt":report.get("createdAt"),"recordCount":len(report.get("records",[])),"reportedErrors":report.get("errors",[]),"changedInputs":changed_sources})
    for rec in report.get("records", []):
        key = (rec["group"],rec["stateIndex"],rec["device"])
        if key not in latest_checks or report["createdAt"] > latest_checks[key][0]:
            latest_checks[key]=(report["createdAt"],rel,rec,changed_sources)

uncovered_checks = []
failed_checks = []
stale_checks = []
for (group,index), state in states.items():
    for device in ("desktop","mobile"):
        key = (group,index,device)
        if key not in latest_checks:
            uncovered_checks.append(key)
            continue
        date, rel, record, changed = latest_checks[key]
        check = record.get("checks",{})
        if any(check.get("rootOverflow",[])) or check.get("outsideControls") or check.get("images"):
            failed_checks.append({"key":key,"report":rel,"checks":check})
        if changed:
            stale_checks.append({"key":key,"report":rel,"changedInputs":changed})
        file = record.get("file")
        if file:
            inspect_asset(dict(record, record=rel),"ui_render")
    for field in ("desktopPng","mobilePng"):
        if state.get(field) and not exists(state[field]):
            issues.append({"type":"missing_ui_state_png", "group":group,"index":index,"file":state[field]})

result = {
    "auditAt":datetime.now(timezone.utc).isoformat(),
    "readOnly":True,
    "snapshotInputs":{str(path.relative_to(BASE)):digest(path) for path in (manifest_path,ledger_path,BASE/"records/inventory-units.json",BASE/"records/inventory-ui.json")},
    "manifestStatus":manifest.get("status"),
    "units":{"required":len(expected_units),"mapped":len(actual_ids),"uniqueIds":len(set(actual_ids)),"missing":missing_units,"extra":extra_units,"duplicates":duplicate_ids,"nonVisualMappings":manifest.get("nonVisualUnits",[]),"uniquePrimaryPngs":len({row.get("file") for row in actual_units})},
    "ui":{"requiredGroups":len(expected_ui),"mappedGroups":len(ui_ids),"missingGroups":sorted(expected_ui-set(ui_ids)),"stateFamilies":len(states),"latestRenderChecks":len(latest_checks),"uncoveredChecks":uncovered_checks,"failedLatestChecks":failed_checks,"staleLatestCheckCount":len(stale_checks),"staleCheckSample":stale_checks[:8],"reports":report_summaries},
    "checkedAssetCount":len(checked_assets),
    "checkedProvenanceRecordCount":len(checked_records),
    "assetIssues":issues,
    "historicalSourceReferences":historical_sources,
    "runtimeIntegrationVerified":manifest.get("runtimeIntegrationVerified"),
    "snapshotConclusion":"incomplete" if missing_units or extra_units or duplicate_ids or issues or uncovered_checks or failed_checks or stale_checks else "artifacts_consistent_runtime_not_verified"
}
OUT.mkdir(parents=True,exist_ok=True)
(OUT/"delivery-audit.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"conclusion":result["snapshotConclusion"],"units":result["units"],"uiGroups":len(ui_ids),"uiStates":len(states),"renderChecks":len(latest_checks),"uncoveredChecks":len(uncovered_checks),"failedChecks":len(failed_checks),"staleChecks":len(stale_checks),"checkedAssets":len(checked_assets),"assetIssues":issues[:15],"issueCount":len(issues)},ensure_ascii=False,indent=2))
