"""Export verified art into fixed upstream source geometry, retaining honest derivation records."""
import json,hashlib,shutil,sys
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image,ImageEnhance,ImageOps,ImageDraw
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parent
sys.path.insert(0,str(ROOT/'records'))
from pixel_tools import components
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
inventory=read(HERE/'source-inventory.json')['assets'];kit={Path(a['file']).stem:a for a in read(ROOT/'ui/kit/manifest.json')['assets']}
outroot=HERE/'compat';outroot.mkdir(exist_ok=True)
results=[];unmapped=[]
def derivation(p):
    for ext in ['.derived.json','.generation.json']:
        q=p.with_name(p.name+ext)
        if q.exists():return q.relative_to(ROOT).as_posix()
    return 'ui/kit/manifest.json' if p.parent==ROOT/'ui/kit' else None
def origin(p):return {'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'record':derivation(p)}
def fit(p,size,pad=0):
    im=Image.open(p).convert('RGBA');im=im.crop(im.getbbox());im.thumbnail((max(1,size[0]-pad*2),max(1,size[1]-pad*2)),Image.Resampling.LANCZOS)
    out=Image.new('RGBA',size);out.alpha_composite(im,((size[0]-im.width)//2,(size[1]-im.height)//2));return out
def shade(im,state):
    alpha=im.getchannel('A');rgb=im.convert('RGB')
    if state=='disabled':rgb=ImageEnhance.Color(rgb).enhance(.15);rgb=ImageEnhance.Brightness(rgb).enhance(.8)
    elif state=='down':rgb=ImageEnhance.Brightness(rgb).enhance(.8)
    elif state=='over':rgb=ImageEnhance.Brightness(rgb).enhance(1.15)
    elif state=='red':
        rgb=ImageOps.colorize(ImageOps.grayscale(rgb),'#6a2530','#ffe2ac')
    out=rgb.convert('RGBA');out.putalpha(alpha);return out
def resize_nine(source,size):
    """Resample nine regions, preserving source border art independently of center."""
    im=Image.open(source).convert('RGBA');entry=kit[source.stem];l,b,r,t=map(int,entry['borderLeftBottomRightTop'])
    if not any((l,b,r,t)):return im.resize(size,Image.Resampling.LANCZOS)
    sw,sh=im.size;dw,dh=size
    sx=[0,l,sw-r,sw];sy=[0,t,sh-b,sh]
    dl=max(1,min(dw//3,round(l*dh/sh)));dr=max(1,min(dw//3,round(r*dh/sh)))
    dt=max(1,min(dh//3,round(t*dw/sw)));db=max(1,min(dh//3,round(b*dw/sw)))
    dx=[0,dl,dw-dr,dw];dy=[0,dt,dh-db,dh]
    out=Image.new('RGBA',size)
    for yy in range(3):
        for xx in range(3):
            if dx[xx+1]>dx[xx] and dy[yy+1]>dy[yy]:
                region=im.crop((sx[xx],sy[yy],sx[xx+1],sy[yy+1])).resize((dx[xx+1]-dx[xx],dy[yy+1]-dy[yy]),Image.Resampling.LANCZOS);out.paste(region,(dx[xx],dy[yy]))
    return out
def state_for(n):
    return next((s for s in ['disabled','down','over','red']if s in n),'normal')
def icon_path(key):
    key={'cancel':'close','trash-16':'trash','logic':'logic-node'}.get(key,key)
    if key=='ranai':return HERE/'special/ranai.png'
    p=HERE/'icons'/f'{key}.png'
    if p.exists():return p
    p=ROOT/'ui/kit'/f'icon-{key}.png'
    return p if p.exists() else None
technical={
 'alpha-bg.png':'Alpha checkerboard conveys actual image transparency; changing its neutral contrast would obscure editor alpha.',
 'alpha-bg-line.png':'Alpha checkerboard strip used by color/opacity controls; neutral functional pattern.',
 'whiteui.png':'White tint primitive; Styles.java:104-110 and editor palette dynamically multiply user-selected colors.',
 'clear.png':'Transparent drawing primitive; exact zero-alpha data required.',
 'selection.png':'One-pixel tint primitive; fixed dimensions and color multiplication.',
 'cursor.png':'4x4 caret/selection marker; exact tiny white mask, distinct from styled OS cursor.',
 'slider.png':'1x8 line/stretch primitive; geometry is the control mask.',
 'bar.9.png':'White progress-fill tint mask; runtime controls fill/team/stat color; keeping exact mask avoids multiplying jade into diagnostic colors.',
 'bar-top.9.png':'White progress cap tint mask; paired with runtime-tinted bar.9.png.',
 'white-pane.9.png':'White recolorable panel mask; renderer supplies its semantic tint.',
 'underline-white.9.png':'White recolorable underline mask; exact stretch and padding metadata retained.',
 'block-border.png':'Rotated white construction outline corner; exact 32px placement geometry, runtime team/validity color.',
 'block-middle.png':'Construction placement center mask; exact center/hotspot and runtime tint.',
 'block-select.png':'CoreBlock.java:827 rotates this corner four times around selectable core bounds.',
 'place-arrow.png':'Directional placement overlay mask; runtime tint and rotation; geometry preserved.',
 'schematic-background.png':'Repeating neutral transparency/empty schematic background, SchematicsDialog.java:744.'}
# Special heads retain identity from the original guide. The previously generated frog is not the ranai replacement.
source=HERE/'source/13-special-identities.png';a=np.array(Image.open(source).convert('RGBA'));h,w=a.shape[:2];cells=[[]for _ in range(4)]
for g in components(a[:,:,3]>=16,min_area=28):
    x0,y0,x1,y1=g['bbox'];i=min(1,int((y0+y1)/2*2/h))*2+min(1,int((x0+x1)/2*2/w));cells[i].append(g)
for i,key in enumerate(['alphaaaa','ranai','nomap','crater']):
    mask=np.zeros((h,w),dtype=bool)
    for g in cells[i]:
        for y,x0,x1 in g['runs']:mask[y,x0:x1]=True
    clean=a.copy();clean[:,:,3]=np.clip(np.rint((a[:,:,3].astype(float)-8)*255/237),0,255).astype(np.uint8);clean[~mask]=0
    im=Image.fromarray(clean);bbox=im.getbbox();cut=im.crop(bbox);out=Image.new('RGBA',(cut.width+24,cut.height+24));out.alpha_composite(cut,(12,12));p=HERE/'special'/f'{key}.png';p.parent.mkdir(exist_ok=True);out.save(p)
    p.with_name(p.name+'.derived.json').write_text(json.dumps({'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'derivedFrom':origin(source),'operation':{'kind':'authorized_alpha_component_crop_padding','sourceBox':list(bbox),'grid':[2,2],'cell':i,'resampling':False,'alphaCutoff':16,'padding':12},'actualModel':None,'actualQuality':None},indent=2)+'\n')
# Hand-painted controls use independent full components, not hard cuts along grid boundaries.
source=HERE/'source/14-control-details.png';a=np.array(Image.open(source).convert('RGBA'));h,w=a.shape[:2];cells=[[]for _ in range(8)]
for g in components(a[:,:,3]>=16,min_area=28):
    x0,y0,x1,y1=g['bbox'];i=min(1,int((y0+y1)/2*2/h))*4+min(3,int((x0+x1)/2*4/w));cells[i].append(g)
for i,key in enumerate(['check-off','check-on','scroll-vertical','scroll-horizontal','slider-knob','inventory','underline-red','progress-fill']):
    mask=np.zeros((h,w),dtype=bool)
    for g in cells[i]:
        for y,x0,x1 in g['runs']:mask[y,x0:x1]=True
    assert mask.sum()>100,key
    clean=a.copy();clean[:,:,3]=np.clip(np.rint((a[:,:,3].astype(float)-8)*255/237),0,255).astype(np.uint8);clean[~mask]=0
    im=Image.fromarray(clean);bbox=im.getbbox();cut=im.crop(bbox);out=Image.new('RGBA',(cut.width+24,cut.height+24));out.alpha_composite(cut,(12,12));p=HERE/'controls'/f'{key}.png';p.parent.mkdir(exist_ok=True);out.save(p)
    p.with_name(p.name+'.derived.json').write_text(json.dumps({'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'derivedFrom':origin(source),'operation':{'kind':'authorized_alpha_component_crop_padding','sourceBox':list(bbox),'grid':[4,2],'cell':i,'resampling':False,'alphaCutoff':16,'padding':12},'actualModel':None,'actualQuality':None},indent=2)+'\n')
for entry in inventory:
    path=entry['sourcePath'];name=Path(path).name;stem=Path(path).stem;ref=ROOT/entry['localReference'];out=outroot/path;out.parent.mkdir(parents=True,exist_ok=True)
    dims=entry.get('sourceSize');src=None;im=None;op=None;reuse=False;extra=[]
    if name in ['fdroid.png','itchio.png']:
        src=ref;reuse=True;op={'kind':'byte_exact_attributed_brand_mark','reason':'Official third-party service mark retained to identify its destination; not a new generated asset.'}
    elif name in technical and ('/sprites/ui/'in path or '/blocks/extra/'in path or name=='schematic-background.png'):
        src=ref;reuse=True;op={'kind':'byte_exact_technical_texture','reason':technical[name],'sourceEvidence':entry['sourceGitBlob']}
    elif path.startswith('ios/')or path=='android/ic_launcher-web.png'or '/assets/icons/icon.'in path:
        src=HERE/'source/05-app-icon.png'
        if path.endswith('.icns'):
            im=Image.open(src).convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS);im.save(out,format='ICNS');op={'kind':'platform_icon_container','sourceNativeSize':list(Image.open(src).size),'sizes':[16,32,64,128,256,512,1024],'resampling':'LANCZOS'}
        else:im=Image.open(src).convert('RGB').resize(tuple(dims),Image.Resampling.LANCZOS);op={'kind':'platform_icon_downsample','resampling':'LANCZOS','sourceNativeSize':list(Image.open(src).size)}
    elif '/sectors/'in path:
        src=HERE/'sectors'/name;im=fit(src,tuple(dims),1);op={'kind':'contain_downsample','resampling':'LANCZOS','semanticKey':stem}
    elif '/icons/'in path and path.startswith('core/assets-raw/icons/'):
        src=icon_path(stem)
        if src:im=fit(src,tuple(dims));op={'kind':'contain_downsample','resampling':'LANCZOS','semanticKey':stem,'usage':'Original icon canvas size. Full-color HD master is supplied separately; original monochrome font glyphs are retained for legibility.'}
    elif '/fontgen/extra/'in path:
        src=ref;reuse=True;op={'kind':'byte_exact_technical_font_glyph','reason':'Original monochrome glyph preserves inner semantic marks, contour holes and font metrics. A filled silhouette of a colored medallion loses these details. New full-color bitmap icon is delivered separately.'}
    elif '/assets/cursors/'in path:
        src=icon_path(stem);im=Image.new('RGBA',tuple(dims));ori=Image.open(ref).convert('RGBA');box=ori.getbbox();part=fit(src,(box[2]-box[0],box[3]-box[1]));im.alpha_composite(part,(box[0],box[1]));op={'kind':'cursor_fit_original_bounds','sourceBounds':list(box),'canvasSize':dims,'resampling':'LANCZOS','hotspot':'Original canvas placement retained; OS hotspot integration requires runtime verification.'}
    elif name=='logo.png':src=HERE/'brand/title-logo.png';im=fit(src,tuple(dims));op={'kind':'contain_downsample','resampling':'LANCZOS','exactTitle':'MINDUSTRY'}
    elif name=='error.png':src=icon_path('missing');im=fit(src,tuple(dims));op={'kind':'contain_downsample','semanticKey':'missing-resource','resampling':'LANCZOS'}
    elif stem in ['cat','ranai','alphaaaa','nomap','crater','logic-node']:
        src=HERE/'special'/name if stem in ['ranai','alphaaaa','nomap','crater']else icon_path(stem);im=fit(src,tuple(dims));op={'kind':'contain_downsample','semanticKey':stem,'resampling':'LANCZOS'}
    elif name.endswith('.9.png'):
        n=name[:-6];state=state_for(n)
        key='button_primary' if n.startswith('button')else 'stat_field' if 'underline'in n or 'scroll'in n or 'slider'in n or 'sideline'in n else 'window_frame'
        src=ROOT/'ui/kit'/f'{key}.png';ori=Image.open(ref).convert('RGBA');w,h=ori.size
        content=shade(resize_nine(src,(w-2,h-2)),state)
        if n in ['inventory','underline-red']:
            src=HERE/'controls'/f'{n}.png';art=Image.open(src).convert('RGBA');art=art.crop(art.getbbox())
            if n=='underline-red':
                # Preserve the original input-error underline location and alpha while using saturated red art.
                box=ori.crop((1,1,w-1,h-1)).getchannel('A').getbbox();content=Image.new('RGBA',(w-2,h-2))
                content.paste(art.resize((box[2]-box[0],box[3]-box[1]),Image.Resampling.LANCZOS),box[:2])
            else:content=art.resize((w-2,h-2),Image.Resampling.LANCZOS)
        # Preserve the original geometric and opacity contract; hand-painted pixels replace the interior material.
        arr=np.array(content);orig=np.array(ori)[1:-1,1:-1];arr[:,:,3]=np.minimum(arr[:,:,3],orig[:,:,3]);content=Image.fromarray(arr)
        im=ori.copy();im.paste(content,(1,1))
        op={'kind':'nine_slice_skin_resample_with_original_metadata','skinBordersLeftBottomRightTop':kit[key]['borderLeftBottomRightTop'],'sourceCanvas':dims,'preserved':'All four 1px metadata rows byte-exact; interior alpha clipped to original geometry. Nine source regions independently resampled.','stateTransform':state,'resampling':'LANCZOS'};extra=[origin(ref)]
    elif name.startswith('check-'):
        state=state_for(stem);on=stem.startswith('check-on');src=HERE/'controls'/('check-on.png'if on else 'check-off.png')
        im=shade(fit(src,tuple(dims),1),state)
        op={'kind':'checkbox_skin_composite','stateTransform':state,'checked':on,'resampling':'LANCZOS'}
    elif name.startswith('scroll-knob')or name.startswith('slider-knob'):
        key='slider-knob'if name.startswith('slider')else 'scroll-horizontal'if 'horizontal'in name else 'scroll-vertical'
        src=HERE/'controls'/f'{key}.png';im=fit(src,tuple(dims));im=shade(im,state_for(stem));op={'kind':'contain_control_skin','stateTransform':state_for(stem),'resampling':'LANCZOS'}
    elif name in ['info-banner.png','discord-banner.png']:
        src=ROOT/'ui/kit/button_primary.png';im=resize_nine(src,tuple(dims));op={'kind':'nine_slice_banner_skin','resampling':'LANCZOS'}
        if name=='info-banner.png':
            info=icon_path('info');overlay=fit(info,(dims[1]-8,dims[1]-8));im.alpha_composite(overlay,(8,4));extra=[origin(info)]
        else:op['usage']='Blank service banner surface; destination/brand label supplied by game UI.'
    if src is None:
        unmapped.append(path);continue
    if reuse:shutil.copyfile(src,out)
    elif im is not None and not path.endswith('.icns'):im.save(out)
    assert out.exists(),path
    if out.suffix=='.png':
        check=Image.open(out);check.verify();check=Image.open(out);assert list(check.size)==dims,(path,check.size,dims)
    r={'sourcePath':path,'sourceGitBlob':entry['sourceGitBlob'],'file':out.relative_to(ROOT).as_posix(),'sha256':sha(out),'sourceSize':dims,'derivedFrom':[origin(src),*extra],'operation':op,'disposition':'verified_technical_reuse'if reuse else 'derived_from_styled_art','status':'exported_pending_visual_review','runtime':'unverified','actualModel':None,'actualQuality':None}
    out.with_name(out.name+'.derived.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');results.append(r)
report={'schemaVersion':1,'status':'exported_pending_review','required':len(inventory),'mapped':len(results),'unmapped':unmapped,'assets':results}
(HERE/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Review at game source sizes and a 4x nearest zoom for the actual runtime silhouette.
visual=[r for r in results if r['file'].endswith('.png') and not '/sectors/'in r['sourcePath'] and not r['sourcePath'].startswith('ios/')]
for page in range((len(visual)+47)//48):
    group=visual[page*48:(page+1)*48];canvas=Image.new('RGB',(1440,6*170),'#19302e');draw=ImageDraw.Draw(canvas)
    for i,r in enumerate(group):
        p=ROOT/r['file'];im=Image.open(p).convert('RGBA');im.thumbnail((130,120));im=im.resize((min(130,im.width*3),min(120,im.height*3)),Image.Resampling.NEAREST)
        x=i%8*180;y=i//8*170;canvas.paste(im,(x+(180-im.width)//2,y+3),im);draw.text((x+6,y+130),Path(r['sourcePath']).name,fill='#eadfc6')
    canvas.save(HERE/f'qa/compat-{page+1:02d}.jpg',quality=96)
print(json.dumps({'required':len(inventory),'mapped':len(results),'unmapped':unmapped,'reused':sum(x['disposition']=='verified_technical_reuse'for x in results)}))
