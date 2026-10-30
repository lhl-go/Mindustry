from pathlib import Path
import json,datetime,hashlib
root=Path(__file__).resolve().parents[1]
p=root/'characters/02-alchemy-engineer-clean.png.derived.json'
d=json.loads(p.read_text(encoding='utf-8'))
d['validation'].update(visualReview='passed_on_light_dark_and_neutral_alpha_composites',visualEvidence='records/character-alpha-qa.jpg',reviewedBy='root',reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),notes='Retained subject RGB unchanged. No visible fringe or isolated outer specks on actual alpha composite; invisible RGB in the raw source was not treated as opaque image content.')
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
resolution={'sourceAcceptance':'records/acceptance-first-batch.json','resolvedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'issues':[
 {'id':'CHAR-EDGE-01','status':'closed_in_final_export','file':d['file'],'sha256':d['sha256'],'evidence':str(p.relative_to(root)).replace('\\','/')},
 {'id':'CHAR-ALPHA-02','status':'closed_in_final_export','file':d['file'],'evidence':'records/character-alpha-qa.jpg'},
 {'id':'HUD-CATEGORY-01','status':'closed_in_native_control_layout','evidence':'ui/preview/?id=UI-002&state=0','resolution':'Defense category contains only defensive buildings; AI concept preserved as design reference.'},
 {'id':'HUD-DIRECTION-02','status':'removed_from_delivered_hud','evidence':'ui/preview/?id=UI-002&state=0','resolution':'Native HUD crop excludes the erroneous directional arrows; markers are separate controls.'},
 {'id':'NATIVE-SIZE-01','status':'reported_host_output_limitation','requested':[2560,1440],'actual':[1672,941],'resampled':False},
 {'id':'NATIVE-SIZE-02','status':'reported_host_output_limitation','requested':[2048,2048],'actualSource':[1254,1254],'finalCanvas':[1328,1328],'resampled':False,'note':'Larger final canvas is transparent padding, not higher native detail.'}
 ],'runtimeIntegrationVerified':False}
(root/'records/first-batch-resolution.json').write_text(json.dumps(resolution,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Character final export accepted; historical initial review preserved.')
