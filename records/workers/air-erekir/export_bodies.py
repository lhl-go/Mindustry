from pipeline import *
SPECS={
 '07-air-utility-body':[('mega',[5,475,540,950]),('incite',[550,485,980,950])],
 '08-tank-body':[('stell',[50,70,460,440]),('locus',[535,25,995,455]),('precept',[1025,25,1520,490]),('vanquish',[5,500,505,965]),('conquer',[495,475,1040,990])],
 '09-walker-body':[('cleroi',[515,60,1030,485]),('anthicus',[1130,5,1440,530]),('tecta',[55,495,540,995])],
 '12-walker-body-correction':[('merui',[80,30,885,877]),('collaris',[905,5,1690,880])],
 '10-erekir-carrier-body':[('quell',[35,90,765,845]),('disrupt',[765,55,1745,880])],
 '11-assault-body-corrected':[('zenith',[20,50,685,700]),('antumbra',[685,90,1420,685]),('eclipse',[1420,0,2165,724])]
}
def cut(source,box,target):
 with Image.open(source) as im: arr=np.array(im.convert('RGBA').crop(box))
 labels,parts=connected(arr[:,:,3]>=32)
 keep=labels==parts[0]['label'];p=np.pad(keep,1)
 keep=np.logical_or.reduce([p[y:y+keep.shape[0],x:x+keep.shape[1]] for y in range(3) for x in range(3)])
 arr[:,:,3][~keep]=0;arr[:,:,3][arr[:,:,3]<16]=0;arr[:,:,3][arr[:,:,3]>=245]=255;arr[arr[:,:,3]==0,:3]=0
 im=Image.fromarray(arr);trim=im.getbbox();im=im.crop(trim)
 out=Image.new('RGBA',(im.width+32,im.height+32));out.alpha_composite(im,(16,16));target.parent.mkdir(parents=True,exist_ok=True);out.save(target)
 return dict(cropRegion=box,trimBoundsInRegion=list(trim),padding=16,width=out.width,height=out.height,alphaLowThreshold=16,opaqueThreshold=245,keepLargestConnectedComponent=True,dilatePixels=1)
layers=[]
for stem,specs in SPECS.items():
 source=ROOT/'units/air-erekir/source'/(stem+'.png')
 for id,box in specs:
  suffix='-body-v2.png' if stem=='12-walker-body-correction' else '-body.png'
  target=ROOT/'units/air-erekir/layers'/(id+suffix);op=cut(source,box,target)
  rec=dict(schemaVersion=1,id=id+'-body',file=target.relative_to(ROOT).as_posix(),sha256=sha(target),width=op['width'],height=op['height'],mode='RGBA',format='PNG',derivedFrom=[dict(file=source.relative_to(ROOT).as_posix(),sha256=sha(source),generationRecord=source.relative_to(ROOT).as_posix()+'.generation.json')],operation=dict(type='native_pixel_crop_and_alpha_cleanup',**op),upsampled=False,anchorNormalized=[0.5,0.5],facing='north',actualModel=None,actualQuality=None,sourceModelEvidence='See native generation record; host exact model and quality undisclosed.')
  write(target.with_name(target.name+'.generation.json'),rec)
  layers.append(dict(id=id,file=rec['file'],role='body',size=[op['width'],op['height']],generationRecord=rec['file']+'.generation.json',sha256=rec['sha256'],anchorNormalized=[0.5,0.5],facing='north',completeUnderpaint=True))
write(HERE/'body-layers.json',layers)
thumb=250;cols=6;rows=3;sheet=Image.new('RGB',(cols*270,rows*290),(230,225,211));d=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
for i,a in enumerate(layers):
 im=Image.open(ROOT/a['file']).convert('RGBA');im.thumbnail((thumb,thumb));tile=Image.new('RGBA',(thumb,thumb),((30,40,40) if i%3==0 else ((245,240,223) if i%3==1 else (120,120,120)))+(255,));tile.alpha_composite(im,((thumb-im.width)//2,(thumb-im.height)//2));x=i%cols*270+10;y=i//cols*290+10;sheet.paste(tile.convert('RGB'),(x,y));d.text((x,y+254),a['id']+' body',font=font,fill=(20,60,50))
sheet.save(ROOT/'units/air-erekir/body-contact.png')
print(json.dumps({'bodyCount':len(layers)}))
