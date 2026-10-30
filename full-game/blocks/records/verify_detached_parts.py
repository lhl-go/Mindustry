"""Integrity audit for the 28 separately produced native parts; does not edit pixels."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'full-game/blocks'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
read = lambda p: json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p, value):
    Path(p).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

manifest = read(OUT / 'parts-manifest.json')
assert manifest['nativePartCount'] == len(manifest['assets']) == 28
assert len({a['id'] for a in manifest['assets']}) == 28
checks = []
edge_contacts = []
for asset in manifest['assets']:
    path = ROOT / asset['file']
    record = read(ROOT / asset['generationRecord'])
    assert sha(path) == asset['sha256'] == record['sha256']
    with Image.open(path) as image:
        assert image.mode == 'RGBA'
        pixels = np.array(image)
        size = list(image.size)
    assert size == asset['nativeSize'] == record['nativeSize']
    assert np.count_nonzero(pixels[:, :, 3]) > 1000
    assert not np.any(pixels[:16, :, 3])
    assert not np.any(pixels[-16:, :, 3])
    assert not np.any(pixels[:, :16, 3])
    assert not np.any(pixels[:, -16:, 3])
    assert not np.any(pixels[pixels[:, :, 3] == 0])
    assert record['operation']['scale'] == 1
    assert record['operation']['newPaintedDetail'] is False
    source = record['derivedFrom'][0]
    assert sha(ROOT / source['file']) == source['sha256']
    generation = read(ROOT / source['generationRecord'])
    assert generation['sha256'] == source['sha256']
    assert generation['actualModel'] is None and generation['actualQuality'] is None
    assert sha(ROOT / generation['evidence']['receipt']) == generation['evidence']['receiptSha256']
    original = np.array(Image.open(ROOT / source['file']).convert('RGBA'))
    x0, y0, x1, y1 = record['operation']['cellBox']
    sx0, sy0, sx1, sy1 = record['operation']['subjectBoxInCell']
    cropped = original[y0 + sy0:y0 + sy1, x0 + sx0:x0 + sx1].copy()
    core = pixels[16:-16, 16:-16]
    assert core.shape == cropped.shape
    keep = core[:, :, 3] > 0
    assert np.array_equal(core[:, :, :3][keep], cropped[:, :, :3][keep])
    expected_alpha = cropped[:, :, 3].copy()
    expected_alpha[expected_alpha >= 245] = 255
    assert np.array_equal(core[:, :, 3][keep], expected_alpha[keep])
    touch = record['sourceEdgeContactPixels']
    if any(touch.values()):
        edge_contacts.append({'id': asset['id'], 'pixels': touch, 'note': record['sourceEdgeNote']})
    checks.append({'id': asset['id'], 'file': asset['file'], 'sha256': asset['sha256'],
                   'nativeSize': size, 'sourceSha256': source['sha256'],
                   'decodeHashDimensionsProvenancePaddingAndNativePixels': 'pass'})
    asset['status'] = 'native_art_static_reviewed_runtime_unverified'

assert edge_contacts == [{'id': 'core-thruster-large-part',
    'pixels': {'left': 0, 'top': 3, 'right': 0, 'bottom': 0},
    'note': 'Source has three alpha>=16 pixels at the uppermost decorative apex. All four nozzle modules are present;16px padding adds no missing art or generated detail.'}]
contacts = []
for board in manifest['boards']:
    for background in ('light', 'dark'):
        path = OUT / 'qa' / (board['name'] + '-' + background + '.jpg')
        derived = read(str(path) + '.derived.json')
        assert sha(path) == derived['sha256']
        assert all(sha(ROOT / item['file']) == item['sha256'] for item in derived['sourceInputs'])
        contacts.append({'file': path.relative_to(ROOT).as_posix(), 'sha256': sha(path),
                         'actualVisualReview': 'pass'})

report_path = OUT / 'qa/detached-parts-review.json'
report = {
    'schema': 'mindustry-detached-parts-static-review-v1',
    'reviewedAt': datetime.now(timezone.utc).isoformat(),
    'nativeParts': 28,
    'status': 'passed_static_art_and_integrity_runtime_unverified',
    'visualReviewEvidence': 'All four final light/dark contact sheets were opened with view_image and actually inspected after the 28 exports completed.',
    'visualObservations': [
        'All 28 parts are separately identifiable, with consistent jade, ivory and warm gold painting.',
        'No visible exterior colored speckles, grid dividers, neighboring subjects or opaque background remain in the reviewed light/dark contacts.',
        'Fine metal edges, internal details and the translucent reactor ring remain visible; the ring is intentionally soft and luminous.',
        'Large core thruster has all four nozzle modules; its decorative apex touched the source top at three pixels. Transparent padding is not reconstructed art.'
    ],
    'orientationObservations': {
        'core-thruster-small-part': 'native nozzle openings face screen right',
        'core-thruster-medium-part': 'native nozzle openings face screen right',
        'core-thruster-large-part': 'native nozzle openings face screen left',
        'integrationRequirement': 'Compatibility exports must follow each original renderer convention; native art is not pre-oriented or mirrored.'
    },
    'sourceEdgeContacts': edge_contacts,
    'contactSheets': contacts,
    'assets': checks,
    'runtimeIntegrationVerified': False,
    'mainManifestModified': False,
    'compatOutputsModified': False,
    'pixelEditsInThisAudit': False
}
write(report_path, report)
manifest['status'] = 'native_art_static_reviewed_runtime_unverified'
manifest['staticReview'] = {'file': report_path.relative_to(ROOT).as_posix(), 'sha256': sha(report_path)}
write(OUT / 'parts-manifest.json', manifest)
print(json.dumps({'parts': len(checks), 'checks': 'passed',
                  'partsManifestSha256': sha(OUT / 'parts-manifest.json'),
                  'reviewSha256': sha(report_path),
                  'nativeWidthRange': [min(a['nativeSize'][0] for a in checks), max(a['nativeSize'][0] for a in checks)],
                  'nativeHeightRange': [min(a['nativeSize'][1] for a in checks), max(a['nativeSize'][1] for a in checks)],
                  'sourceEdgeContacts': edge_contacts}))
