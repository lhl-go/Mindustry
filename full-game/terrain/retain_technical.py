from pathlib import Path
from PIL import Image
import json,hashlib,shutil,datetime
H=Path(__file__).resolve().parent;R=H.parents[1];commit='17012d61d9e4c3cbd9820d87e81c24495486ac53'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
inv=json.loads((H/'inventory.json').read_text(encoding='utf-8'));m=json.loads((H/'manifest.json').read_text(encoding='utf-8'))
license_dest=H/'licenses/Mindustry-LICENSE.txt';license_dest.parent.mkdir(exist_ok=True);shutil.copyfile(R/'records/reference-ui-sources/LICENSE-Mindustry-v160.7',license_dest)
added=[]
for e in inv['entries']:
 n=e['region'];p=e['officialPath'];reason=None;source=[]
 if n.startswith('character-overlay'):
  reason='Semantic 64-glyph reduced alphabet plus editor icons; 6-bit character and 2-bit rotation encoding must retain readable exact glyph identities. Official geometry retained, no AI art claimed.';source=['core/src/mindustry/world/blocks/environment/CharacterOverlay.java']
 elif n.startswith('rune-overlay'):
  reason='Semantic 109-rune encoded alphabet per faction plus icons; overlayData maps exact glyph indices to Unicode offset0x142B. Official geometry retained, no AI art claimed.';source=['core/src/mindustry/world/blocks/environment/RuneOverlay.java']
 elif e['category']=='cliff_mask':
  reason='Binary cliff silhouette masks are combined into256 data-indexed cliffmask regions and tinted by floor.mapColor in Cliff.drawBase; geometric connectivity mask retained, no AI surface painting claimed.';source=['core/src/mindustry/world/blocks/environment/Cliff.java','tools/src/mindustry/tools/Generators.java']
 elif e['category']=='edge_mask':
  reason='Floor transition edge stencil multiplies actual floor pixels; exact3x3 edge geometry and alpha coverage retained to avoid breaking blending. New floor material supplies appearance.';source=['core/src/mindustry/world/blocks/environment/Floor.java']
 elif n.startswith('colored-floor') or n.startswith('colored-wall'):
  reason='User-configurable color/tint carrier with exact auto-tile alpha connectivity; neutral shape and channels retained for runtime recoloring, not treated as newly painted terrain.';source=['core/src/mindustry/world/blocks/environment/ColoredFloor.java','core/src/mindustry/world/blocks/environment/ColoredWall.java']
 elif p.startswith('core/assets/sprites/') and n in ['caustics','clouds','distortAlpha','fog','noise','noiseAlpha','rays']:
  reason='Technical scalar/alpha modulation texture for procedural rendering; frequency, channel and repeat behavior retained byte-exact. These are runtime shader inputs, not replacement scenic paintings.';source=['core/src/mindustry/graphics/Shaders.java','core/src/mindustry/graphics/CacheLayer.java']
 elif p.startswith('core/assets-raw/') and n in ['clear-editor','data-patch-reserved-env','empty','env-error','remove-ore','remove-wall','space']:
  reason='Editor sentinel/removal/error or blank procedural shader carrier; preserving exact function marker/transparent coverage prevents changing editor/runtime semantics. Official utility asset retained and disclosed.';source=['core/src/mindustry/content/Blocks.java','core/src/mindustry/graphics/Shaders.java']
 if not reason:continue
 src=H/e['officialSource']['file'];dest=H/'assets'/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
 with Image.open(dest) as im:
  size=list(im.size);a=im.convert('RGBA').getchannel('A');ext=a.getextrema();mode=im.mode
 rec={'schemaVersion':1,'file':dest.relative_to(R).as_posix(),'sha256':sha(dest),'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'kind':'official_technical_asset_retained','artSource':'official_retained_technical','newlyDrawn':False,'sourceRepository':'https://github.com/Anuken/Mindustry','sourceCommit':commit,'officialPath':p,'officialGitBlobSha1':e['gitBlobSha1'],'upstreamUrl':'https://github.com/Anuken/Mindustry/blob/'+commit+'/'+p,'sourceSha256':sha(src),'byteIdenticalToOfficial':dest.read_bytes()==src.read_bytes(),'width':size[0],'height':size[1],'mode':mode,'alphaRange':list(ext),'reason':reason,'technicalEvidence':source,'license':{'file':license_dest.relative_to(R).as_posix(),'sha256':sha(license_dest),'identifier':'GPL-3.0 repository LICENSE','note':'Preserved upstream LICENSE and source attribution; no claim of new AI ownership over retained upstream pixels.'},'actualModel':None,'actualQuality':None,'unverifiedReason':'Not AI-generated: exact upstream technical resource retained.'}
 rp=dest.with_name(dest.name+'.source.json');rp.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 entry={'officialPath':p,'region':n,'file':rec['file'],'record':rp.relative_to(R).as_posix(),'sha256':rec['sha256'],'size':size,'artSource':'official_retained_technical','newlyDrawn':False,'category':'technical_retained','originalCategory':e['category'],'opaque':ext==(255,255),'status':'official_technical_byte_verified','reason':reason,'runtimeIntegrationVerified':False}
 m['assets']=[x for x in m['assets'] if x['officialPath']!=p]+[entry];e['status']=entry['status'];e['outputFile']=entry['file'];added.append(p)
m['mappedCount']=len(m['assets']);m['countsByArtSource']={k:sum(e['artSource']==k for e in m['assets']) for k in set(e['artSource'] for e in m['assets'])}
for p,obj in [(H/'manifest.json',m),(H/'inventory.json',inv),(H/'records/technical-retained.json',{'count':len(added),'paths':added,'notNewAIArt':True,'sourceCommit':commit})]:p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'retained':len(added),'totalMapped':m['mappedCount'],'counts':m['countsByArtSource']}))
