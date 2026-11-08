"""Independent read-only unit body/part source comparison. No image processing."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re

BASE=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
def read(rel): return json.loads((BASE/rel).read_text(encoding="utf-8-sig"))
inventory=read("records/inventory-units.json")
official={u["id"]:u for u in inventory["units"]}
source_dir=BASE/"records/reference-unit-sources"
sources={name:(source_dir/name).read_text(encoding="utf-8-sig").splitlines() for name in ("UnitTypes.java","Blocks.java")}

def strip_comments(text):
    return re.sub(r"/\*.*?\*/|//[^\n]*",lambda m:"\n"*m.group().count("\n"),text,flags=re.S)

def source_text(unit):
    definition=unit["definition"]
    start,end=definition["line"],definition["endLine"]
    lines=sources[definition["source"]][start-1:end]
    for other in inventory["units"]:
        child=other["definition"]
        if child["source"]==definition["source"] and start<child["line"] and child["endLine"]<end:
            for i in range(child["line"]-start,child["endLine"]-start+1):
                lines[i]=""
    return strip_comments("\n".join(lines))

def object_body(text,position):
    begin=text.find("{",position)
    if begin<0:return ""
    level=0;quoted=False;escape=False
    for end in range(begin,len(text)):
        char=text[end]
        if quoted:
            if escape:escape=False
            elif char=="\\":escape=True
            elif char=='"':quoted=False
        elif char=='"':quoted=True
        elif char=="{":level+=1
        elif char=="}":
            level-=1
            if level==0:return text[begin:end+1]
    return text[begin:]

unit_rows=[]
worker_rows=[]
for worker in ("special","root-builders","air-erekir","serpulo-ground-naval"):
    manifest_rel=f"records/workers/{worker}/manifest.json"
    if not (BASE/manifest_rel).exists():
        worker_rows.append({"worker":worker,"manifestMissing":True})
        continue
    manifest=read(manifest_rel)
    worker_rows.append({"worker":worker,"manifest":manifest_rel,"status":manifest.get("status"),"sha256":hashlib.sha256((BASE/manifest_rel).read_bytes()).hexdigest()})
    for asset in manifest.get("assets",[]):
        uid=asset["id"]
        if uid not in official:continue
        unit=official[uid]
        text=source_text(unit)
        named_weapons=[]
        for match in re.finditer(r'new\s+(\w*Weapon)\s*\(\s*"([^"]+)"\s*\)',text):
            weapon=object_body(text,match.end())
            rotate=re.search(r"\brotate\s*=\s*(true|false)",weapon)
            recoil=re.search(r"\brecoil\s*=\s*([\d.]+)f?",weapon)
            named_weapons.append({"region":match.group(2),"class":match.group(1),"rotate":rotate.group(1)=="true" if rotate else False,"recoil":float(recoil.group(1)) if recoil else 1.5,"sourceLine":unit["definition"]["line"]+text[:match.start()].count("\n")})
        parts=[]
        for match in re.finditer(r'new\s+RegionPart\s*\(\s*"([^"]+)"\s*\)',text):
            body=object_body(text,match.end())
            movement=re.findall(r"\b(move\w*|rotation|mirror)\s*=\s*([^;]+);",body)
            parts.append({"suffix":match.group(1),"movement":dict(movement),"sourceLine":unit["definition"]["line"]+text[:match.start()].count("\n")})
        segment_match=re.search(r"\bsegments\s*=\s*(\d+)",text)
        leg_match=re.search(r"\blegCount\s*=\s*(\d+)",text)
        roles=[]
        for layer in asset.get("layers",[]):
            if isinstance(layer,dict):roles.append(layer.get("role") or layer.get("kind") or str(layer))
        required=[]
        if named_weapons:required.append("independent named weapon region(s), for mount rotation and/or recoil")
        if parts:required.append("independent RegionPart image(s) for source-declared motion")
        if leg_match:required.append("independent joint/leg/foot/base representation for procedural legs")
        if segment_match:required.append(f"{segment_match.group(1)} independent crawler segment images")
        if unit.get("mobility")=="biped_mech":required.append("independent mech base/leg regions")
        status=asset.get("status",manifest.get("status",""))
        declared_complete=not any(word in status for word in ("in_progress","pending_review","blocked","needs_fix"))
        findings=[]
        if required and not roles:
            findings.append({"severity":"pending_required_parts" if not declared_complete else "confirmed_missing_declared_parts", "message":"Composite unit PNG exists but worker declares no independent layer mapping.","requirements":required})
        if segment_match:
            segment_layers=[l for l in asset.get("layers",[]) if isinstance(l,dict) and "segmentIndex" in l]
            if len(segment_layers)!=int(segment_match.group(1)):
                findings.append({"severity":"confirmed_segment_count_mismatch", "required":int(segment_match.group(1)),"mapped":len(segment_layers)})
        unit_rows.append({"id":uid,"worker":worker,"workerStatus":manifest.get("status"),"assetStatus":status,"compositeFile":asset.get("file"),"roles":roles,"layerFileCount":len(asset.get("layerFiles",[])),"source":unit["definition"],"mobility":unit.get("mobility"),"namedWeapons":named_weapons,"regionParts":parts,"legCount":int(leg_match.group(1)) if leg_match else None,"segments":int(segment_match.group(1)) if segment_match else None,"requirements":required,"findings":findings,"runtimeStatus":"Not evaluated; engine integration alone is not an art failure."})

confirmed=[dict(id=u["id"],finding=f) for u in unit_rows for f in u["findings"] if f["severity"].startswith("confirmed")]
pending=[dict(id=u["id"],finding=f) for u in unit_rows for f in u["findings"] if f["severity"].startswith("pending")]
result={"auditedAt":datetime.now(timezone.utc).isoformat(),"readOnly":True,"scope":"Semantic part completeness only; earlier file hashes and UI rendering are not repeated.","upstreamVersion":"v160.7","workers":worker_rows,"mappedUnitsReviewed":len(unit_rows),"confirmedIssues":confirmed,"pendingParts":pending,"units":unit_rows,"knownSourceRendererEvidence":[{"file":"records/reference-unit-sources/UnitType.java","line":1902,"fact":"drawCrawl draws each segment image at the unit center with source-defined motion; transparent image offsets express the assembled shape."},{"file":"records/coordinator-audit/Weapon-v160.7.java","line":218,"url":"https://github.com/Anuken/Mindustry/blob/v160.7/core/src/mindustry/type/Weapon.java#L218","fact":"Weapon draw applies mount rotation and recoil before drawing its named region."}],"limitations":["Mask/outline/team-cell atlas pipeline not executed; no failure is inferred from that absence.","Source-level named region presence does not prove a separate picture is needed for nameless effect-only weapons; those are not flagged.","Per-part shape completeness and dynamic registration require visual/source review; no image transforms or runtime tests performed."]}
(OUT/"unit-semantics-audit.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"mappedReviewed":len(unit_rows),"confirmedIssues":confirmed,"pendingRequiredPartUnits":[u["id"] for u in unit_rows if u["findings"]],"workers":worker_rows},ensure_ascii=False,indent=2))
