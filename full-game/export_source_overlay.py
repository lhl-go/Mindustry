"""Export verified replacement files into a NEW source-tree overlay directory.

Usage: python full-game/export_source_overlay.py --output /absolute/new/folder
This does not alter a game checkout or claim to build/run Mindustry.
"""
import argparse,json,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    coverage=read(ROOT/'full-game/coverage.json')
    if coverage['status']!='all_source_images_verified':raise SystemExit('Full art coverage is not verified yet; no overlay exported.')
    output=args.output.resolve()
    if output.exists():raise SystemExit('Output directory must not exist; existing files are never overwritten.')
    rows=[{'source':a['file'],'target':a['sourcePath'],'sha256':a['sha256']}for a in coverage['assets']]
    runtime=read(ROOT/'full-game/runtime-visuals/manifest.json')
    rows.extend({'source':a['file'],'target':a['sourcePath'],'sha256':a['sha256']}for a in runtime['assets'])
    units=read(ROOT/'full-game/units/manifest.json')
    rows.extend({'source':a['file'],'target':a['sourceTreePath'],'sha256':a['sha256']}for a in units.get('additionalAtlasRegions',[])if a.get('copyIntoSourceTree'))
    targets=set()
    for r in rows:
        dest=(output/r['target']).resolve()
        if not dest.is_relative_to(output)or dest in targets:raise ValueError('Unsafe/duplicate destination: '+r['target'])
        targets.add(dest)
        if sha(ROOT/r['source'])!=r['sha256']:raise ValueError('Changed source: '+r['source'])
    output.mkdir(parents=True)
    for r in rows:
        dest=output/r['target'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/r['source'],dest)
        assert sha(dest)==r['sha256']
    report={'sourceCommit':coverage['sourceCommit'],'files':rows,'count':len(rows),'runtimeIntegrationVerified':False,'note':'Source tree replacements and technical dependencies only. Run the original Mindustry asset/atlas build in its own matching checkout. UI layout design previews are a separate deliverable.'}
    (output/'ART-OVERLAY-MANIFEST.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(output),'verifiedFiles':len(rows),'runtimeIntegrationVerified':False}))
if __name__=='__main__':main()
