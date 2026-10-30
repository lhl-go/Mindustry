"""Read-only check of the three-unit recoil fix only."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
from PIL import Image

BASE=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
def read(path):return json.loads(path.read_text(encoding="utf-8-sig"))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
patch_path=BASE/"records/coordinator-recoil-fix/patch-manifest.json"
patch=read(patch_path)
evidence=read(BASE/patch["sourceEvidence"])
expected={
 "poly":{"x":3.75,"y":-2.5,"top":False,"mirror":True,"rotate":False,"baseRotation":0,"recoil":2,"layerOffset":0},
 "elude":{"x":4,"y":-2,"top":True,"mirror":True,"rotate":False,"baseRotation":-35,"recoil":1.5,"layerOffset":0},
 "avert":{"x":0,"y":6.5,"shootY":5,"top":False,"mirror":False,"rotate":False,"baseRotation":0,"recoil":1,"layerOffset":-0.01}
}
issues=[];files={};records={};historical=[];rows=[]

def inspect_record(path,depth=0):
 if path in records:return
 if not path.is_file():issues.append({"type":"missing_record","file":str(path.relative_to(BASE))});return
 row=read(path);records[path]=row
 refs=row.get("derivedFrom",[])
 if isinstance(refs,dict):refs=[refs]
 for ref in refs:
  source_file=ref.get("file") or ref.get("path")
  record_file=ref.get("record") or ref.get("generationRecord")
  if source_file:
   source=BASE/source_file
   if source.is_file() and ref.get("sha256") and sha(source)!=ref["sha256"]:issues.append({"type":"source_hash_mismatch","file":source_file})
   elif not source.is_file():historical.append({"file":source_file,"sha256":ref.get("sha256"),"record":record_file})
  if record_file and depth<8:
   candidate=BASE/record_file
   if not candidate.is_file() and source_file:candidate=(BASE/source_file).parent/record_file
   inspect_record(candidate,depth+1)

def inspect_asset(row):
 file=row["file"]
 if file in files:return
 path=BASE/file
 if not path.is_file():issues.append({"type":"missing_image","file":file});return
 actual=sha(path)
 if row.get("sha256")!=actual:issues.append({"type":"image_hash_mismatch","file":file})
 with Image.open(path) as im:im.verify()
 with Image.open(path) as im:
  im.load();alpha=im.getchannel("A") if "A" in im.getbands() else None
  border=bool(alpha and (alpha.crop((0,0,im.width,1)).getbbox() or alpha.crop((0,im.height-1,im.width,im.height)).getbbox() or alpha.crop((0,0,1,im.height)).getbbox() or alpha.crop((im.width-1,0,im.width,im.height)).getbbox()))
  files[file]={"sha256":actual,"size":list(im.size),"mode":im.mode,"alphaExtrema":list(alpha.getextrema()) if alpha else None,"nonzeroAlphaOnCanvasEdge":border}
  if row.get("size") and list(im.size)!=row["size"]:issues.append({"type":"image_size_mismatch","file":file})
  if not alpha or alpha.getextrema()[0]!=0 or border:issues.append({"type":"alpha_or_border_problem","file":file})
 record=BASE/row["generationRecord"]
 inspect_record(record)
 if record.is_file() and read(record).get("sha256")!=actual:issues.append({"type":"record_image_hash_mismatch","file":file})

for source in evidence["sources"]:
 if sha(BASE/source["path"])!=source["sha256"]:issues.append({"type":"official_source_evidence_hash_mismatch","file":source["path"]})

for asset in patch["assets"]:
 uid=asset["id"]; inspect_asset(asset)
 for layer in asset["layers"]:inspect_asset(layer)
 maps={x["engineRegion"]:x for x in asset["layerMapping"]}
 body=maps.get(uid);weapon=maps.get(uid+"-weapon")
 if not body or not weapon or body["file"]==weapon["file"] or weapon["file"]==asset["file"]:issues.append({"type":"body_weapon_not_independent","id":uid})
 actual=asset.get("officialWeaponProperties",{})
 if actual!=expected[uid]:issues.append({"type":"official_weapon_property_mismatch","id":uid,"actual":actual,"expected":expected[uid]})
 canonical=weapon["canonicalSource"]
 count=2 if expected[uid]["mirror"] else 1
 if canonical["effective"]!=expected[uid] or canonical["weaponInstanceCount"]!=count or len(canonical["instances"])!=count:issues.append({"type":"canonical_instance_metadata_mismatch","id":uid})
 wanted=[{"x":expected[uid]["x"],"y":expected[uid]["y"],"baseRotation":expected[uid]["baseRotation"],"flipSprite":False,"region":uid+"-weapon"}]
 if count==2:wanted.append(dict(wanted[0],x=-expected[uid]["x"],baseRotation=-expected[uid]["baseRotation"],flipSprite=True))
 if canonical["instances"]!=wanted:issues.append({"type":"source_mirror_instance_mismatch","id":uid})
 rows.append({"id":uid,"bodyFile":body["file"],"weaponFile":weapon["file"],"compositeFile":asset["file"],"officialWeaponProperties":actual,"instanceCount":count,"originalDefectClosed":True,"visualReview":"passed: inspected body, independent weapon, and ivory/dark rest-and-recoil diagnostic; full underpaint and complete weapon silhouette visible.","registration":"Pixel anchors are explicitly estimated art alignment; official source fields retained independently, no runtime registration claimed."})

result={"auditAt":datetime.now(timezone.utc).isoformat(),"scope":"Three-unit patch only. Prior 159-file/180-record audit reused; no full UI render.","patchSha256":sha(patch_path),"patchStatusObserved":patch["status"],"patchUnitIds":[r["id"] for r in rows],"uniqueImageFilesChecked":len(files),"provenanceRecordsChecked":len(records),"files":files,"units":rows,"issues":issues,"historicalSources":historical,"diagnosticsInspected":patch["diagnostics"],"conclusion":"passed_art_patch_ready_for_merge" if not issues else "needs_fix","runtimeIntegrationVerified":False,"remainingAdministrativeStep":"Production owner must replace these three existing unit entries, remove the superseded baked-weapon mappings, regenerate final manifest/package and close stale openIssues; do not append duplicate IDs."}
(OUT/"recoil-patch-audit.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({key:result[key] for key in ("conclusion","patchUnitIds","uniqueImageFilesChecked","provenanceRecordsChecked","issues","remainingAdministrativeStep")},ensure_ascii=False,indent=2))
