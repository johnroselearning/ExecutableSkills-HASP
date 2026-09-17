"""Pilot 1b: bind interface-only parser and new artifacts to unchanged Pilot 1 loop."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import pilot_runner as original
from pilot1b_parser import parse_action
HERE = Path(__file__).resolve().parent
OUT = HERE/'results/pilot1b'


def freeze_pilot1b():
    if (OUT/'manifest.json').exists():
        raise SystemExit('Existing Pilot 1b preserved; refusing rerun/overwrite.')
    historical = json.loads((OUT/'historical_parser_contract.json').read_text())
    assert len(historical)==5 and all(r['validation_result']=='valid' for r in historical)
    previous = json.loads((HERE/'results/pilot1/manifest.json').read_text())
    for path, digest in previous['source_hashes'].items():
        source = Path(path) if Path(path).is_absolute() else HERE/path
        assert hashlib.sha256(source.read_bytes()).hexdigest()==digest, path
    hashes = {}
    names = ['pilot1b_parser.py','pilot1b_runner.py','test_pilot1b_parser.py',
             'pilot_runner.py','native_adapter.py','evaluator.py','oracle.py','hypotheses.py',
             'actions.py','PILOT1B_PROTOCOL.md','PILOT1_PROTOCOL.md']
    paths = [HERE/name for name in names]
    paths += [Path(path) for path in previous['source_hashes'] if Path(path).is_absolute()]
    paths += list((HERE.parents[2]/'skills/executable/docs/support').rglob('*.md'))
    for source in paths:
        key = str(source.relative_to(HERE)) if source.is_relative_to(HERE) else str(source)
        hashes[key] = hashlib.sha256(source.read_bytes()).hexdigest()
        # Preserve source-relative directory layout to avoid support card filename collisions.
        relative = source.relative_to(HERE.parents[2])
        dest = OUT/'frozen'/relative
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,dest)
    manifest = {'run_id':'pilot1b','started':original.stamp(),'status':'running',
        'worlds':list(original.HYPOTHESES),'trials':5,'arms':original.ARMS,'episodes':80,
        'initial_case':'initial','max_steps':8,'model':original.MODEL,'options':original.OPTIONS,
        'think':False,'source_hashes':hashes,
        'methodological_difference':'Whole-output fenced-JSON acceptance only; no decoding changes.',
        'original_sources_verified_against_pilot1':True,
        'selector':'native pf_select_eval unchanged prompt/parser',
        'rendered_provider_prompt':'Not exposed by Ollama; exact messages and saved model template available.'}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest

if __name__=='__main__':
    if sys.argv[1:] != ['--run-approved-pilot1b']:
        raise SystemExit('Usage: pilot1b_runner.py --run-approved-pilot1b')
    original.OUT = OUT
    original.parse_action = parse_action
    original.freeze = freeze_pilot1b
    sys.argv[1:] = ['--run-approved-pilot1']
    original.main()
