"""Read-only audit of archived evidence. Never invokes EDA or opens the job queue."""

from collections import Counter
from dataclasses import asdict
from decimal import Decimal
import csv
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
WORKSPACE = PROJECT.parent
sys.path.insert(0, str(PROJECT / 'backend/src'))
from area_lab.infrastructure.catalog import build_catalog
from area_lab.infrastructure.liberty import read_cells


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(65536), b''):
            value.update(block)
    return value.hexdigest()


def require(condition, description):
    if not condition:
        raise AssertionError(description)


def main():
    assets = PROJECT / 'assets'
    designs, technologies = build_catalog(assets)
    profiles = {d.id: d for d in designs}
    tech = {t.id: t for t in technologies}
    cells = {t.id: read_cells(assets / t.liberty_file) for t in technologies}
    snapshot = json.loads((assets / 'manifest.json').read_text())
    for source in snapshot['files']:
        require(digest(assets / source['snapshot']) == source['sha256'], source['snapshot'])
        require(digest(WORKSPACE / source['original']) == source['sha256'], source['original'])
    root = PROJECT / 'docs/validation/dpu-matrix-20261018'
    results = []
    integer_vectors = 0
    for path in sorted(root.glob('*/*/report.json')):
        report = json.loads(path.read_text())
        manifest = json.loads((path.parent / 'manifest.json').read_text())
        require(report['manifest'] == manifest, str(path)+' manifest mismatch')
        design = profiles[report['design_id']]
        technology = tech[report['technology_id']]
        recorded = dict(manifest['design'])
        recorded.setdefault('compilation', 'files')
        require(recorded == json.loads(json.dumps(asdict(design))), str(path)+' profile mismatch')
        require(manifest['technology'] == asdict(technology), str(path)+' technology mismatch')
        require(digest(assets / technology.liberty_file) == manifest['liberty_sha256'], 'Liberty hash')
        for relative, value in manifest['source_sha256'].items():
            require(digest(assets / relative) == value, relative)
        for filename, key in [('stimuli.txt','stimuli_sha256'),('rtl-results.txt','rtl_results_sha256'),('vectors.txt','vectors_sha256')]:
            require(digest(path.parent / filename) == manifest['functional_test'][key], filename)
        stimuli = (path.parent / 'stimuli.txt').read_text().splitlines()
        outputs = (path.parent / 'rtl-results.txt').read_text().splitlines()
        vectors = (path.parent / 'vectors.txt').read_text().splitlines()
        require(len(stimuli)==len(outputs)==len(vectors)==256, 'vector count')
        for stimulus, output, vector in zip(stimuli,outputs,vectors,strict=True):
            require(vector == f'{stimulus} {output}', 'vector binding')
            require(len(output)==design.result_bits//4 and all(c in '0123456789abcdefABCDEF' for c in output), 'undefined RTL')
            if design.family == 'integer':
                words = [int(w,16) for w in stimulus.split()]
                sign = 1 << (design.operand_bits-1)
                signed = [(w^sign)-sign for w in words[:8]]
                expected = (sum(a*b for a,b in zip(signed[:4],signed[4:],strict=True))+words[8]) & ((1<<design.result_bits)-1)
                require(int(output,16)==expected, 'independent integer oracle')
                integer_vectors += 1
        stat = json.loads((path.parent / 'stat.json').read_text())['design']
        counts = {row['name']: row['count'] for row in report['cells']}
        require(counts == stat['num_cells_by_type'], 'stat cell counts')
        require(sum(counts.values())==report['total_cells']==stat['num_cells'], 'total count')
        category_area = Counter()
        category_counts = Counter()
        for row in report['cells']:
            cell = cells[technology.id][row['name']]
            subtotal = cell.area * row['count']
            require(cell.category == row['category'], 'cell category')
            require(abs(subtotal-Decimal(str(row['total_area']))) < Decimal('0.0000001'), 'cell subtotal')
            require(cell.area == Decimal(str(row['unit_area'])), 'unit area')
            category_area[cell.category] += subtotal
            category_counts[cell.category] += row['count']
        total = sum(category_area.values(),Decimal(0))
        error = max(abs(total-Decimal(str(report['total_area']))),abs(total-Decimal(str(stat['area']))))
        require(error<Decimal('0.0000001'), 'area mismatch')
        require(category_area['combinational']==Decimal(str(report['combinational_area'])), 'logic area')
        require(category_area['flip_flop']+category_area['latch']==Decimal(str(report['sequential_area'])), 'sequential area')
        require(all(category_counts[k]==n for k,n in report['cell_counts'].items()), 'category counts')
        require(not stat['num_memories'] and not stat['num_processes'] and not stat['num_submodules'], 'incomplete synthesis')
        require(report['cell_counts']['latch']==report['cell_counts']['macro']==0, 'unexpected state')
        require(0 < report['cell_counts']['flip_flop'] <= design.declared_register_bits, 'wrapper state')
        if design.expected_flip_flops is not None:
            require(report['cell_counts']['flip_flop']==design.expected_flip_flops,'integer FF count')
        log = gzip.decompress((path.parent/'run.log.gz').read_bytes())
        require(log.count(b'VALIDATION_OK 256')==2,'RTL and mapped log markers')
        for token in [b'--out=verilog',b'yosys -s synth.ys',b'iverilog -g2012',b'vvp mapped_sim']:
            require(token in log,'missing logged stage '+str(token))
        for unit in manifest.get('compilation',{}).get('units',[]):
            require(digest(path.parent/unit['file'])==unit['sha256'],'derived unit hash')
        results.append(dict(design_id=design.id,technology_id=technology.id,
                            combinational_area=report['combinational_area'],sequential_area=report['sequential_area'],
                            total_area=report['total_area'],cells=report['total_cells'],ff=report['cell_counts']['flip_flop'],
                            vectors=256,area_error=float(error),report_sha256=digest(path),
                            log_sha256=hashlib.sha256(log).hexdigest(),
                            proof=str(path.relative_to(PROJECT)),
                            mapped_netlist_archived=(path.parent/'mapped.v').is_file()))
    expected={(d.id,t.id) for d in designs if d.id!='lns16' for t in technologies}
    require({(r['design_id'],r['technology_id']) for r in results}==expected, 'missing completed case')
    code_hashes={str(p.relative_to(PROJECT)):digest(p) for p in sorted((PROJECT/'backend/src').rglob('*.py'))}
    for p in [PROJECT/'Dockerfile',PROJECT/'compose.yaml',PROJECT/'scripts/prepare_assets.py']:
        code_hashes[str(p.relative_to(PROJECT))]=digest(p)
    result=dict(date='2026-10-19',method='read_only_archived_artifact_audit_no_eda',
                completed_cases=len(results),planned_cases=len(designs)*len(technologies),
                missing_cases=[f'lns16/{t.id}' for t in technologies],
                input_files_verified=len(snapshot['files']),integer_vectors_recomputed=integer_vectors,
                rtl_vector_executions_documented=256*len(results),mapped_vector_executions_documented=256*len(results),
                max_area_error=max(r['area_error'] for r in results),cases=results,code_sha256_at_review=code_hashes,
                limits=['No fresh EDA execution; log markers are retained evidence, not a new simulation.',
                        'Compact archive lacks mapped.v, mapped.json, design.v and cells_sim.v; cell counts are checked against stat.json.',
                        'SHA-256 establishes byte identity to retained inputs, not third-party certification or anti-tamper proof.',
                        'No independent mathematical oracle for FXP/FP/Posit/LNS; no formal equivalence or STA.',
                        'Current source hash recorded now was not captured as a complete application/container digest at old execution time.',
                        'PPA timing, power, floorplan, routing and manufactured chip area not assessed.'])
    (HERE/'auditoria_evidencias.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    with (HERE/'auditoria_evidencias.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(results[0]));writer.writeheader();writer.writerows(results)
    print(json.dumps({k:v for k,v in result.items() if k not in ['cases','code_sha256_at_review','limits']},ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
