import json,hashlib,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(HERE/'manifest.json');inv={a['sourcePath']:a for a in read(HERE/'source-inventory.json')['assets']};changed=[]
for a in m['assets']:
    if '/fontgen/extra/'in a['sourcePath']:
        src=ROOT/inv[a['sourcePath']]['localReference'];dest=ROOT/a['file'];shutil.copyfile(src,dest)
        a.update(sha256=sha(dest),derivedFrom=[{'file':src.relative_to(ROOT).as_posix(),'sha256':sha(src),'record':None}],operation={'kind':'byte_exact_technical_font_glyph','reason':'Original monochrome glyph preserves inner semantic marks, contour holes and font metrics. A filled silhouette of a colored medallion loses these details. New full-color bitmap icon is delivered separately.'},disposition='verified_technical_reuse')
        write(dest.with_name(dest.name+'.derived.json'),a);changed.append(a['sourcePath'])
    elif a.get('operation',{}).get('usage','').startswith('Native icon source size.'):
        a['operation']['usage']='Original icon canvas size. Full-color HD master supplied separately; original monochrome font glyph retained for legibility.'
        write((ROOT/a['file']).with_name(Path(a['file']).name+'.derived.json'),a)
write(HERE/'manifest.json',m);print(json.dumps({'correctedFontSources':len(changed),'reused':sum(a['disposition']=='verified_technical_reuse'for a in m['assets'])}));assert len(changed)==7
