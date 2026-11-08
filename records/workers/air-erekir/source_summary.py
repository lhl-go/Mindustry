from pathlib import Path
import re,json
root=Path(__file__).resolve().parents[3]
s=(root/'records/reference-unit-sources/UnitTypes.java').read_text(encoding='utf-8')
names='flare horizon zenith antumbra eclipse mono poly mega quad oct stell locus precept vanquish conquer merui cleroi anthicus tecta collaris elude avert obviate quell disrupt evoke incite emanate'.split()
out=[]
for name in names:
    m=re.search(r'        '+name+r' = new \w+\(',s)
    rest=s[m.start():]
    nxt=re.search(r'\n        \w+ = new \w+\(',rest[1:])
    block=rest[:nxt.start()+1] if nxt else rest
    props=re.findall(r'(?:legCount|flying|hovering|hitSize|armor|buildSpeed|mineTier|payloadCapacity|rotate|mirror)\s*=\s*[^;]+;',block)
    weapons=re.findall(r'new (?:\w+Weapon|Weapon)\(([^)]*)\)',block)
    out.append(dict(name=name,line=s[:m.start()].count('\n')+1,properties=props[:40],weapons=weapons))
(Path(__file__).parent/'source-summary.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
