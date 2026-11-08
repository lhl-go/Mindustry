"""Read embedded provenance strings without changing PNGs or asserting signature trust."""
from pathlib import Path
import hashlib
import json
import re
import struct

ROOT = Path(__file__).resolve().parents[1]
for folder in ('ui','characters'):
    for path in (ROOT/folder).glob('*.png'):
        raw = path.read_bytes()
        offset = 8
        cabx = None
        while offset + 12 <= len(raw):
            length = struct.unpack('>I',raw[offset:offset+4])[0]
            kind = raw[offset+4:offset+8]
            payload = raw[offset+8:offset+8+length]
            offset += length+12
            if kind == b'caBX':
                cabx = payload
                break
        evidence = dict(file=path.relative_to(ROOT).as_posix(), caBXPresent=cabx is not None,
                        cryptographicSignatureVerified=False, exactModelVersion=None, quality=None)
        if cabx:
            strings = [s.decode('ascii') for s in re.findall(rb'[ -~]{5,}',cabx)
                       if re.search(rb'gpt|softwareAgent|claim_generator_info|OpenAI Media Service',s,re.I)]
            evidence.update(chunkSha256=hashlib.sha256(cabx).hexdigest(),chunkByteLength=len(cabx),
                rawRelevantPrintableStrings=strings,
                softwareAgentName='ChatGPT' if b'dnamegChatGPT' in cabx else None,
                softwareAgentVersion='gpt-image' if b'gversionigpt-image' in cabx else None,
                interpretation='Embedded software-agent tag identifies only gpt-image generically. It does not identify GPT Image 2.5/Sunburst/max; actualModel and actualQuality remain null.')
        evidence_path=ROOT/'records'/(path.stem+'.embedded-provenance.json')
        evidence_path.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        record_path=path.with_name(path.name+'.generation.json')
        record=json.loads(record_path.read_text(encoding='utf-8'))
        record['evidence']['embeddedProvenance']=evidence_path.relative_to(ROOT).as_posix()
        record['evidence']['embeddedModelMetadataFound']=False
        record['evidence']['embeddedSoftwareAgentVersion']=evidence.get('softwareAgentVersion')
        record['evidence']['embeddedProvenanceSignatureVerified']=False
        record['unverifiedReason']='宿主管理，工具未披露精确型号或质量。PNG 内嵌软件代理版本仅为 gpt-image，未给出2.5、Sunburst或max，且本次未验证其加密签名，不能据此确认实际具体型号。'
        record_path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(path.name, 'embedded software tag:', evidence.get('softwareAgentVersion'), '; exact model/quality not confirmed')
