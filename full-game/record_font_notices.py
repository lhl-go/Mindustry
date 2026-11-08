"""Preserve font attribution from unmodified runtime binaries and primary sources."""
import json,hashlib,struct,zlib,re,urllib.request,concurrent.futures
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent.parent;HERE=ROOT/'full-game/runtime-visuals'
OUT=HERE/'font-notices';OUT.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
records=[]
for asset in read(HERE/'manifest.json')['assets']:
    p=ROOT/asset['file']
    if p.suffix not in ['.ttf','.woff']:continue
    b=p.read_bytes();assert sha(b)==asset['sha256'];tables={}
    if b[:4]==b'wOFF':
        for i in range(struct.unpack_from('>H',b,12)[0]):
            tag,offset,comp,size,_=struct.unpack_from('>4sIIII',b,44+i*20);d=b[offset:offset+comp];tables[tag]=zlib.decompress(d)if comp<size else d
    else:
        for i in range(struct.unpack_from('>H',b,4)[0]):
            tag,_,offset,size=struct.unpack_from('>4sIII',b,12+i*16);tables[tag]=b[offset:offset+size]
    d=tables[b'name'];_,n,offset=struct.unpack_from('>HHH',d,0);names=[];seen=set()
    for i in range(n):
        platform,encoding,language,name,length,o=struct.unpack_from('>HHHHHH',d,6+i*12)
        if name not in [0,1,4,8,9,13,14]:continue
        s=d[offset+o:offset+o+length].decode('utf-16-be'if platform in [0,3]else'latin1',errors='replace')
        if(name,s)in seen:continue
        seen.add((name,s));names.append({'nameId':name,'platformId':platform,'languageId':language,'text':s})
    records.append({'file':asset['file'],'sha256':asset['sha256'],'modifiedByThisPackage':False,'embeddedNames':names})
repos={'fontawesome':'awesome-uni.font','typicons':'typicons.font','zocial':'zocial.font','iconic':'iconic-uni.font','entypo':'entypo','elusive':'elusive.font','mfglabs':'mfglabs.font','brandico':'brandico.font','modernpics':'modernpics.font'}
def fetch(entry):
    name,url,metadata=entry;p=OUT/name
    if p.exists():b=p.read_bytes()
    else:
        b=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mindustry-art-attribution'}),timeout=40).read();p.write_bytes(b)
    result={'url':url,'file':p.relative_to(ROOT).as_posix(),'sha256':sha(b),'retrievedOn':'2026-10-26','sourcePurpose':metadata}
    if name.endswith('.yml'):
        text=b.decode('utf-8');header=re.split(r'^glyphs:',text,flags=re.M)[0]
        result['metadataLines']=[line.strip()for line in header.splitlines()if re.match(r'\s*(author|homepage|license|license_url|copyright|fullname):',line)]
    return result
entries=[(family+'.yml','https://raw.githubusercontent.com/fontello/'+repo+'/master/config.yml','Fontello component attribution; current primary metadata, not proof of the precise embedded glyph revision')for family,repo in repos.items()]
entries += [('FiraCode-OFL.txt','https://raw.githubusercontent.com/tonsky/FiraCode/master/LICENSE','Font project license notice'),('NotoSansCJK-OFL.txt','https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/LICENSE','Font project license notice'),('Proggy-MIT.txt','https://raw.githubusercontent.com/bluescan/proggyfonts/master/LICENSE','Font project license notice')]
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:external=list(pool.map(fetch,entries))
config=read(HERE/'upstream/core/assets-raw/fontgen/config.json');families={s:sum(g.get('src')==s for g in config['glyphs'])for s in sorted({g.get('src')for g in config['glyphs']})}
result={'recordedAt':datetime.now(timezone.utc).isoformat(),'fonts':records,'fontelloSourceFamiliesFromFixedMindustryConfig':families,'primaryNotices':external,'darktechLicenseUrl':'https://creativecommons.org/licenses/by-sa/3.0/','scope':'All six runtime font binaries are exact upstream reuse, with original embedded names and copyright preserved. Metadata snapshots provide attribution, not a new or blanket license for unrelated art.'}
(HERE/'font-notices.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# Runtime font notices','','All six font files are unchanged copies from the fixed Mindustry commit. Exact binary hashes and embedded names are in [font-notices.json](../font-notices.json).','', 'Darktech LDR is by Michał “Neoqueto” Nowak (2012). Its embedded notice specifies [Creative Commons Attribution Share Alike 3.0](https://creativecommons.org/licenses/by-sa/3.0/). No font modification was made in this package.','','Noto Sans JP, Fira Code and ProggyCleanTT notices are preserved in the adjacent license files; original copyright strings remain inside the binary and in the JSON record.','', 'Fontello component metadata listed by the fixed Mindustry font-generation config:','']
for a in external:
    if 'metadataLines'in a:lines.extend(['- ['+Path(a['file']).stem+']('+Path(a['file']).name+'): '+'; '.join(a['metadataLines'])])
lines+=['','Custom glyphs and generated Fontello binaries retain Mindustry provenance. These notices do not replace the component licenses or grant any new license over unrelated generated artwork.']
(OUT/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'fontFiles':len(records),'primaryNoticeFiles':len(external),'fontelloFamilies':families}))
