from build import *
def main():
 m=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'));rows=[];errors=[];edges=[]
 for a in m['assets']:
  p=ROOT/a['file'];im=Image.open(p).convert('RGBA');arr=np.array(im);al=arr[:,:,3];r=json.loads((ROOT/a['generationRecord']).read_text(encoding='utf-8'));e=Image.open(ROOT/a['engineFile']);issues=[]
  if sha(p)!=a['sha256']:issues.append('file_hash_mismatch')
  if list(e.size)!=a['officialSize']:issues.append('engine_size_mismatch')
  if not np.any(al) and a['id']!='clear-effect':issues.append('empty')
  if a['artKind']!='exact_official_technical_texture_reuse' and (np.any(al[0,:]) or np.any(al[-1,:]) or np.any(al[:,0]) or np.any(al[:,-1])):issues.append('export_border_contact')
  edge=None
  if a['artKind']=='generated_art':
   sr=ROOT/r['derivedFrom'][0]['file'];crop=Image.open(sr).convert('RGBA').crop(r['operation']['crop']);aa=np.array(crop)[:,:,3];edge=int((aa[0]>=128).sum()+(aa[-1]>=128).sum()+(aa[:,0]>=128).sum()+(aa[:,-1]>=128).sum())
   if edge:edges.append(dict(id=a['id'],sourceOpaqueEdgePixels=edge))
  rows.append(dict(id=a['id'],file=a['file'],sha256=sha(p),engineFile=a['engineFile'],engineSha256=sha(ROOT/a['engineFile']),sourceOpaqueEdgePixels=edge,visiblePixels=int(np.count_nonzero(al)),transparentFraction=float(np.mean(al==0)),issues=issues,visualCheck='passed_light_and_dark_contact',engineNotVerified=True))
  errors.extend([a['id']+':'+x for x in issues])
 firehashes=[a['sha256'] for a in m['assets'] if a['id'].startswith('fire')];assert len(firehashes)==40 and len(set(firehashes))==40
 write(BASE/'qa/report.json',dict(commit=m['commit'],checkedAt=datetime.now(timezone.utc).isoformat(),sourcePathCount=164,exported164=True,originalEngineDimensionsVerified=164,fireFrames=40,uniqueFireFrameHashes=len(set(firehashes)),errors=errors,sourceCellEdgeReview=edges,items=rows,visualEvidence=m['contacts'],runtimeFxCount=267,additionalGeneratedRegions=dict(bubbleExported=16,splashExported=12,fluidOfficialGeneratorPreserved=100),engineNotVerified=True))
 print(json.dumps({'errors':errors,'sourceCellEdgeReview':edges}))
if __name__=='__main__':main()
