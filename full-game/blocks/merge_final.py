"""Merge the three accepted, disjoint source-path batches without altering their art."""
from export_common import *
from collections import Counter
def main():
 m=read(HERE/'manifest.json');parts=read(HERE/'parts-manifest.json');assets={a['id']:a for a in m['assets']}
 for a in parts['assets']:
  if a['id']in assets:assert assets[a['id']]['sha256']==a['sha256']
  assets[a['id']]=a
 assert len(assets)==301
 batches=[];rows=[];geometry={}
 for name,count in [('root',367),('hud_review',251),('units_air_erekir',141)]:
  p=HERE/'batches'/(name+'.json');b=read(p);assert b['status']=='art_export_complete_runtime_unverified',(name,b['status']);assert len(b['sourceMappings'])==count and not b.get('errors')
  rows+=b['sourceMappings'];batches.append({'file':rel(p),'sha256':sha(p),'sourceCount':count,'review':b.get('review')})
  for a in b.get('integrationGeometryInputs',[]):
   assert sha(ROOT/a['file'])==a['sha256'];geometry[a['file']]=a
 expected={a['sourcePath']for a in ROWS.values()};actual={a['sourcePath']for a in rows}
 assert len(rows)==len(actual)==759 and actual==expected
 for a in rows:
  assert sha(ROOT/a['file'])==a['sha256']and sha(ROOT/a['nativeFile'])==a['nativeSha256']
  im=Image.open(ROOT/a['file']);assert list(im.size)==a['sourceDimensions'];im.verify()
 for a in assets.values():
  assert sha(ROOT/a['file'])==a['sha256'];im=Image.open(ROOT/a['file']);assert list(im.size)==a['nativeSize'];im.verify();a['status']='art_export_complete_runtime_unverified'
 m.update(status='art_export_complete_runtime_unverified',acceptedAt=datetime.now(timezone.utc).isoformat(),requiredSourcePngCount=759,baselineAllBlockSourcePngCount=904,delegatedTurretSourcePngCount=145,nativeMasterCount=len(assets),assets=list(assets.values()),sourceMappings=sorted(rows,key=lambda a:a['sourcePath']),integrationGeometryInputs=list(geometry.values()),acceptedBatches=batches,dispositionCounts=dict(Counter(a['disposition']for a in rows)),runtimeIntegrationVerified=False)
 write(HERE/'manifest.json',m)
 write(HERE/'qa/final-block-validation.json',{'checkedAt':datetime.now(timezone.utc).isoformat(),'status':'passed','sourcePaths':759,'nativeMasters':301,'requiredGeometryInputs':len(geometry),'noDuplicateOrMissingSourcePaths':True,'decodedHashesAndOriginalCanvasesVerified':True,'manifestSha256':sha(HERE/'manifest.json'),'batches':batches,'runtimeIntegrationVerified':False})
 (HERE/'README.md').write_text('# 建筑与运行层素材\n\n本目录覆盖固定 Mindustry v160.7 的 759 个建筑源路径，另 145 个炮塔路径在 `../root-turrets`。301 张原生建筑、连接形状及独立部件保留实际尺寸；兼容输出保持原版画布、锚点、连接几何及运行时图层语义。\n\n`manifest.json` 逐项记录新图派生、原版几何与技术复用，`batches` 及 `qa` 保存实际视检、分层、方向、相位和哈希证据。`integrationGeometryInputs` 是重建技术派生必需的原版几何输入，不能按已消费参考图清除。兼容小图的缩放、着色、清理和组合不算新模型生成或新原生细节。\n\n传送带、推进器、旋转头与旋转指示层分别按源码方向处理；液体窗口、连接与状态及门洞使用已核验的原版透明几何。大型核心推进器原生顶端装饰有 3 个像素触及源板边界，喷嘴完整，未重绘缺失细节。已完成静态素材核验，未声称启动并验收实际游戏客户端。\n',encoding='utf-8')
 print(json.dumps({'sourcePaths':len(rows),'nativeMasters':len(assets),'geometryInputs':len(geometry),'manifestSha256':sha(HERE/'manifest.json')}))
if __name__=='__main__':main()
