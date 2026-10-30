from pathlib import Path
import json,datetime
ROOT=Path(__file__).resolve().parents[1]
def read(f):return json.loads((ROOT/f).read_text(encoding='utf-8-sig'))
def dump(f,d):(ROOT/f).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
f='records/workers/air-erekir/manifest.json';m=read(f);m['priorQaRecord']=m['qaRecord'];m['qaRecord']='records/final-delivery-verification.json';m['contactRecords']=[p+'.derived.json' for p in m['contactSheets']];dump(f,m)
f='records/workers/air-erekir/final-contact.json';d=read(f);d['status']='historical_contact_superseded_after_recoil_merge';d['supersededBy']='units/air-erekir/final-contact.png.derived.json';dump(f,d)
p=ROOT/'records/workers/air-erekir/HANDOFF.md';s=p.read_text(encoding='utf-8');s='# Root merge completion\n\nAll 28 entries are now complete art assets. The three independent recoil patches were merged by root; their former pending issues are closed. Current source of truth is manifest.json and records/recoil-patch-merge.json. Contact sheets were regenerated from the current 28 entries. The original handoff below records the pre-merge state; its 32-image local cleanup limitation remains in effect.\n\n'+s;p.write_text(s,encoding='utf-8')
print('Final unit metadata updated; no image pixels changed.')
