"""Validate the presentation archive and chart provenance without an Office process."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from collections import Counter
import hashlib
import json
import re

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[2]
content=json.loads((HERE/'contenido.json').read_text())
audit=json.loads((HERE/'auditoria_evidencias.json').read_text())
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
with ZipFile(HERE/'Revision_pipeline_ASIC_GIRA.pptx') as archive:
    assert archive.testzip() is None
    for name in archive.namelist():
        if name.endswith('.xml') or name.endswith('.rels'):
            ET.fromstring(archive.read(name))
    slides=[p for p in archive.namelist() if re.fullmatch(r'ppt/slides/slide\d+.xml',p)]
    notes=[p for p in archive.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+.xml',p)]
    charts=sorted(p for p in archive.namelist() if re.fullmatch(r'ppt/charts/chart\d+.xml',p))
    assert len(slides)==len(notes)==len(content['slides'])==53
    assert len(charts)==2
    for i,s in enumerate(content['slides'],1):
        slide=ET.fromstring(archive.read(f'ppt/slides/slide{i}.xml'))
        assert s['title'] in ''.join(slide.itertext()) or s['type']=='cover'
        assert 'EVIDENCIA LOCAL' in ''.join(ET.fromstring(archive.read(f'ppt/notesSlides/notesSlide{i}.xml')).itertext())
    expected=[[r['total_area'] for t in ['ihp130','nangate45','nangate15'] for r in audit['cases'] if r['design_id']=='int8_16' and r['technology_id']==t],
              [r['total_area'] for r in audit['cases'] if r['technology_id']=='nangate45']]
    for name,values in zip(charts,expected,strict=True):
        actual=[float(n.text) for n in ET.fromstring(archive.read(name)).findall('.//c:val/c:numRef/c:numCache/c:pt/c:v',ns)]
        assert actual==values,(name,actual,values)
    logo=(PROJECT.parent/'gira.png').read_bytes()
    assert any(archive.read(p)==logo for p in archive.namelist() if p.startswith('ppt/media/'))
visual=json.loads((HERE/'revision_visual.json').read_text())
assert visual['text_overflow']==[]
proof={'slides':len(slides),'speaker_notes':len(notes),'native_charts_verified':len(charts),
       'original_logo_embedded':True,'xml_and_zip_valid':True,'overflow_findings':0,
       'chart_values_match_audited_reports':True,
       'pptx_sha256':hashlib.sha256((HERE/'Revision_pipeline_ASIC_GIRA.pptx').read_bytes()).hexdigest(),
       'pdf_sha256':hashlib.sha256((HERE/'Revision_pipeline_ASIC_GIRA.pdf').read_bytes()).hexdigest(),
       'office_render_verified':False}
(HERE/'validacion_entregables.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof,indent=2))
