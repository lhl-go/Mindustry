"""Incremental audit for newly finished unit groups; no production mutations."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, re

BASE=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
def read(path):return json.loads(path.read_text(encoding="utf-8-sig"))
inventory=read(BASE/"records/inventory-units.json")
official={row["id"]:row for row in inventory["units"]}
sources={name:(BASE/"records/reference-unit-sources"/name).read_text(encoding="utf-8-sig").splitlines() for name in ("UnitTypes.java","Blocks.java")}
issues=[]; notes=[]; historical=[]; assets_checked={}; records_checked={}; rows=[]; workers=[]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def resolve(record,file,from_record=None):
    for option in (BASE/record, BASE/Path(file).parent/record, (BASE/from_record).parent/record if from_record else BASE/record):
        if option.is_file():return option
    return BASE/record

def provenance(path,depth=0):
    if path in records_checked:return
    if not path.is_file():
        issues.append({"type":"missing_record","record":str(path.relative_to(BASE))});return
    record=read(path); records_checked[path]=record
    refs=record.get("derivedFrom",[])
    if isinstance(refs,dict):refs=[refs]
    for source in refs:
        if not isinstance(source,dict):continue
        file=source.get("file") or source.get("path")
        gen=source.get("generationRecord") or source.get("record")
        if file:
            target=BASE/file
            if target.is_file() and source.get("sha256") and sha(target)!=source["sha256"]:
                issues.append({"type":"source_hash_mismatch","file":file,"record":str(path.relative_to(BASE))})
            elif not target.is_file():
                historical.append({"file":file,"sha256":source.get("sha256"),"record":gen})
        if gen and depth<15:provenance(resolve(gen,file or "",str(path.relative_to(BASE))),depth+1)

def artifact(row):
    file=row.get("file")
    if not file or file in assets_checked:return
    target=BASE/file
    if not target.is_file():issues.append({"type":"missing_image","file":file});return
    actual=sha(target); assets_checked[file]=actual
    if row.get("sha256") and row["sha256"]!=actual:issues.append({"type":"image_hash_mismatch","file":file})
    record=row.get("generationRecord") or row.get("record")
    path=resolve(record,file) if record else next((BASE/(file+suffix) for suffix in (".generation.json",".derived.json") if (BASE/(file+suffix)).is_file()),None)
    if not path:issues.append({"type":"unrecorded_image","file":file});return
    provenance(path)
    if path.is_file():
        data=read(path)
        if data.get("sha256") and data["sha256"]!=actual:issues.append({"type":"record_image_hash_mismatch","file":file})

def definition(unit):
    loc=unit["definition"]; start,end=loc["line"],loc["endLine"]
    lines=sources[loc["source"]][start-1:end]
    for other in official.values():
        child=other["definition"]
        if child["source"]==loc["source"] and start<child["line"] and child["endLine"]<end:
            for i in range(child["line"]-start,child["endLine"]-start+1):lines[i]=""
    text="\n".join(lines)
    return re.sub(r"/\*.*?\*/|//[^\n]*",lambda m:"\n"*m.group().count("\n"),text,flags=re.S)

def body(text,pos):
    begin=text.find("{",pos); level=0; quoted=False;escape=False
    if begin<0:return ""
    for end in range(begin,len(text)):
        c=text[end]
        if quoted:
            if escape:escape=False
            elif c=="\\":escape=True
            elif c=='"':quoted=False
        elif c=='"':quoted=True
        elif c=="{":level+=1
        elif c=="}":
            level-=1
            if level==0:return text[begin:end+1]
    return text[begin:]

for worker in ("serpulo-ground-naval","air-erekir"):
    path=BASE/f"records/workers/{worker}/manifest.json"
    manifest=read(path)
    workers.append({"worker":worker,"status":manifest.get("status"),"sha256":sha(path),"assetCount":len(manifest.get("assets",[]))})
    for asset in manifest.get("assets",[]):
        artifact(asset)
        uid=asset["id"]; unit=official[uid]; text=definition(unit); findings=[]
        for layer in asset.get("layers",[]):
            artifact(layer if isinstance(layer,dict) else {"file":layer})
        for file in asset.get("layerFiles",[]):artifact({"file":file})
        mapping=asset.get("layerMapping",{})
        if isinstance(mapping,list):mapping={item["engineRegion"]:item for item in mapping}
        roles=[x.get("role","") for x in asset.get("layers",[]) if isinstance(x,dict)]
        body_files={x.get("file") for x in asset.get("layers",[]) if isinstance(x,dict) and x.get("role","").startswith("body")}
        named=[]
        for match in re.finditer(r'new\s+(\w*Weapon)\s*\(\s*"([^"]+)"\s*\)',text):
            region=match.group(2); weapon=body(text,match.end()); rotate=re.search(r"\brotate\s*=\s*(true|false)",weapon); recoil=re.search(r"\brecoil\s*=\s*([\d.]+)f?",weapon)
            rotating=rotate.group(1)=="true" if rotate else False
            recoil_value=float(recoil.group(1)) if recoil else 1.5
            source_line=unit["definition"]["line"]+text[:match.start()].count("\n")
            item=mapping.get(region); entries=item if isinstance(item,list) else [item] if item else []
            files={entry.get("file") for entry in entries}
            named.append({"region":region,"sourceLine":source_line,"rotate":rotating,"recoil":recoil_value,"mappedFiles":sorted(file for file in files if file)})
            if not entries:
                findings.append({"type":"missing_named_weapon_mapping","region":region,"sourceLine":source_line})
            elif (rotating or recoil_value>0) and files<=body_files:
                findings.append({"type":"moving_weapon_baked_in_body","region":region,"sourceLine":source_line,"rotate":rotating,"recoil":recoil_value,"mappedFiles":sorted(files),"contractReason":"Source has independently moving weapon; body-only mapping suppresses its art motion."})
        parts=[]
        for match in re.finditer(r'new\s+RegionPart\s*\(\s*"([^"]+)"\s*\)',text):
            suffix=match.group(1)
            matched=[key for key in mapping if key.endswith(suffix)]
            parts.append({"suffix":suffix,"mappedRegions":matched})
            if not matched:findings.append({"type":"missing_region_part_mapping","suffix":suffix,"sourceLine":unit["definition"]["line"]+text[:match.start()].count("\n")})
        leg_match=re.search(r"\blegCount\s*=\s*(\d+)",text)
        if leg_match:
            count=int(leg_match.group(1))
            actual=asset.get("legCount",asset.get("articulation",{}).get("legCount"))
            if actual!=count:findings.append({"type":"leg_count_mismatch","sourceLegCount":count,"mappedLegCount":actual})
            if not any("leg" in role for role in roles) or not any("foot" in role for role in roles):findings.append({"type":"missing_articulated_leg_or_foot_layer","roles":roles})
        if unit.get("mobility")=="biped_mech" and not any("leg" in role for role in roles):findings.append({"type":"missing_biped_leg_layer","roles":roles})
        if unit.get("javaClass")=="TankUnitType" and not any("tread" in role for role in roles):findings.append({"type":"missing_tread_source","roles":roles})
        rows.append({"id":uid,"worker":worker,"assetStatus":asset.get("status"),"mobility":unit.get("mobility"),"roles":roles,"layerFiles":asset.get("layerFiles",[]),"namedWeapons":named,"regionParts":parts,"findings":findings})

ids=[row["id"] for row in rows]
expected={u["id"] for u in official.values() if u.get("independentArtRequired")}
prior=read(OUT/"unit-semantics-audit.json")
reused=[u for u in prior["units"] if u["worker"] in ("special","root-builders")]
all_ids=ids+[u["id"] for u in reused]
semantic=[dict(id=u["id"],finding=f) for u in rows for f in u["findings"]]
pending=[{"worker":w["worker"],"status":w["status"]} for w in workers if "pending" in w["status"] or "progress" in w["status"]]
result={"auditAt":datetime.now(timezone.utc).isoformat(),"readOnly":True,"scope":"New 53 worker units only; prior 15 semantic checks reused, no UI rendering repeated.","workers":workers,"newIndependentUnitIds":len(ids),"newUniqueIds":len(set(ids)),"reusedUnitCount":len(reused),"allUniqueIds":len(set(all_ids)),"missingRequiredUnitIds":sorted(expected-set(all_ids)),"extraIds":sorted(set(all_ids)-expected),"duplicateIds":sorted({unit for unit in all_ids if all_ids.count(unit)>1}),"newImageFilesChecked":len(assets_checked),"provenanceRecordsChecked":len(records_checked),"fileAndRecordIssues":issues,"semanticIssues":semantic,"pendingReviewStates":pending,"historicalSourceReferences":historical,"units":rows,"reusedPriorReview":"records/coordinator-audit/unit-semantics-audit.json","conclusion":"needs_art_semantic_fix" if semantic or issues else "structural_semantics_pass_visual_review_pending" if pending else "structural_semantics_pass_runtime_not_verified"}
(OUT/"new-worker-final-audit.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({key:result[key] for key in ("conclusion","newIndependentUnitIds","allUniqueIds","missingRequiredUnitIds","duplicateIds","newImageFilesChecked","provenanceRecordsChecked","fileAndRecordIssues","semanticIssues","pendingReviewStates")},ensure_ascii=False,indent=2))
