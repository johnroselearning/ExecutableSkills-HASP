"""Offline-only competition checkpoint. No provider client or inference entry point."""
from copy import deepcopy
import hashlib
import itertools
import json
from pathlib import Path
from oracle import Oracle
from evaluator import viable, score_actions
from native_adapter import (IDS, ROOT, load_native, dispatch, policy_messages,
                            selector_messages, revision_messages, menu_text)
HERE = Path(__file__).resolve().parent
OUT = HERE / 'competition_checkpoint'
PATHS = ['A', 'B', 'C', 'D', 'E', 'AB', 'AD', 'BE', 'CE', 'DE']
NEUTRAL = ('Review your proposed diagnostic action once more using only the evidence '
           'already available and return your final action. Use the same single-action JSON format.')
PLACEHOLDER = '<EXACT SHARED BASE PROPOSAL; GENERATED ONLY AFTER APPROVAL>'

def make_public(path, truth='H1'):
    oracle = Oracle(truth)
    for action in path:
        oracle.execute(action)
    return oracle.public_state()

def gates(public):
    from src.skills_agent.skills.program_functions import get_program_function
    ctx = {'question': public['problem'], 'domain': 'support',
           'support_evidence': public['support_evidence'],
           'evidence': '\n'.join(r['observation'] for r in public['history']),
           'action_history': public['history'], 'step_count': 0, 'max_steps': 8,
           '_pf_fire_counts': dict.fromkeys(IDS, 0)}
    result = {}
    for sid in IDS:
        # Independent contexts and all possible proposed action IDs. Native gates
        # do not inspect reason text; source hashes also pin that implementation.
        values = {bool(get_program_function(sid).should_activate(deepcopy(ctx), 'INVESTIGATE',
                  json.dumps({'action': a, 'reason': 'offline gate audit'}))) for a in 'ABCDEF'}
        assert len(values) == 1
        result[sid] = values.pop()
    return result

def main():
    prior = json.loads((HERE/'results/pilot1b/manifest.json').read_text())
    hashes = {}
    for name, expected in prior['source_hashes'].items():
        p = Path(name) if Path(name).is_absolute() else HERE/name
        actual = hashlib.sha256(p.read_bytes()).hexdigest()
        assert actual == expected, f'Pilot 1b source changed: {p}'
        hashes[name] = actual
    execute, library = load_native()
    rows, prompts = [], {}
    for i, path in enumerate(PATHS, 1):
        public = make_public(path)
        gate = gates(public)
        eligible = [sid for sid in IDS if gate[sid]]
        assert len(eligible) >= 2 and len(viable(public['history'])) > 1
        # Every viable world must reproduce this exact snapshot, facts included.
        for world in viable(public['history']):
            assert make_public(path, world) == public
        result = dispatch(execute, public, PLACEHOLDER, eligible, dict.fromkeys(IDS, 0), 0)
        activated = [r['skill_id'] for r in result['records'] if r['activated']]
        assert activated == eligible and len(result['interventions']) == len(eligible)
        scores = score_actions(public['history'], 'H1')
        sid = f'S{i:02d}'
        rows.append({'snapshot': sid, 'oracle_history': list(path), 'public_state': public,
                     'fire_counts': dict.fromkeys(IDS, 0), 'gates': gate, 'eligible': eligible,
                     'number_eligible': len(eligible), 'viable_worlds_offline': viable(public['history']),
                     'offline_scores': scores, 'best_actions': [r['action'] for r in scores if r['rank']==1],
                     'deterministic_C_dispatch_audit': result})
        prompts[sid] = {'A_base_shared': policy_messages(public),
                       'B_selector': selector_messages(public, PLACEHOLDER, menu_text(library)),
                       'B_revision_template': revision_messages(public, PLACEHOLDER, ['<ACTUAL NATIVE INTERVENTIONS IN DISPATCH ORDER>']),
                       'C_revision': revision_messages(public, PLACEHOLDER, result['interventions']),
                       'D_revision': policy_messages(public)+[{'role':'assistant','content':PLACEHOLDER}, {'role':'user','content':NEUTRAL}]}
    assert len({json.dumps(r['public_state'],sort_keys=True) for r in rows}) == 10
    # Exhaustive canonical subsets: no repeated diagnostics, all six oracle actions,
    # all four worlds. Order does not change these consistent cumulative facts.
    coverage=[]
    for n in range(7):
        for path in itertools.combinations('ABCDEF', n):
            for world in ['H1','H2','H3','H4']:
                public=make_public(path,world); gate=gates(public)
                if gate['comparison_experiment'] and gate['binary_isolation']:
                    coverage.append({'path':list(path),'world':world,'viable':viable(public['history'])})
    assert coverage and all(len(r['viable'])==1 for r in coverage)
    # Verify deterministic dispatch and audit did not edit pinned sources.
    for name, expected in hashes.items():
        p=Path(name) if Path(name).is_absolute() else HERE/name
        assert hashlib.sha256(p.read_bytes()).hexdigest()==expected
    OUT.mkdir(exist_ok=True)
    (OUT/'snapshots.json').write_text(json.dumps(rows,indent=2)+'\n')
    (OUT/'prompt_flows.json').write_text(json.dumps(prompts,indent=2)+'\n')
    (OUT/'audit.json').write_text(json.dumps({'model_calls':0,'source_hashes_verified_against_pilot1b':hashes,
        'snapshot_count':len(rows),'two_eligible':sum(r['number_eligible']==2 for r in rows),
        'three_eligible':sum(r['number_eligible']==3 for r in rows),
        'comparison_isolation_subset_checks':coverage,'all_comparison_isolation_states_resolved':True},indent=2)+'\n')
    doc=['# Fixed competition snapshot matrix', '',
         'Offline score = expected eliminations / action cost under the unchanged uniform viable-world evaluator. T/F are actual native wrapper gate results with all fire counts zero.', '',
         'PF1 evidence_collection; PF2 request_id_trace; PF3 comparison_experiment; PF4 dependency_trace; PF5 binary_isolation.', '',
         '| Snapshot | Oracle history / public evidence | Viable worlds (offline) | PF1 | PF2 | PF3 | PF4 | PF5 | Eligible | Scores A / B / C / D / E / F | Best |',
         '|---|---|---|---|---|---|---|---|---:|---|---|']
    for r in rows:
        doc.append('| '+ ' | '.join([r['snapshot'], ''.join(r['oracle_history']), ', '.join(r['viable_worlds_offline']),
            *['T' if r['gates'][sid] else 'F' for sid in IDS], str(r['number_eligible']),
            ' / '.join(f"{s['expected_eliminations_per_cost']:.6g}" for s in r['offline_scores']), ', '.join(r['best_actions'])])+' |')
    doc += ['', '## Exact evidence visible to the model', '', 'The public action menu and exact complete messages are in `prompt_flows.json`. Only problem, observed history (action, observation, cost) and public actions enter policy messages. Structured facts below are native gate inputs, not an additional model message. No world label, score, rank, gate matrix or best action enters model messages.']
    for r in rows:
        doc += ['', '### '+r['snapshot'], '', '```json', json.dumps({'problem':r['public_state']['problem'],
            'observed_history':[{k:h[k] for k in ('action','observation','cost')} for h in r['public_state']['history']]},indent=2), '```',
            '', 'Native gate evidence:', '```json',json.dumps(r['public_state']['support_evidence'],indent=2),'```']
    (OUT/'MATRIX.md').write_text('\n'.join(doc)+'\n')
    print(json.dumps({'snapshots':10,'model_calls':0,'native_sources_unchanged':True,'output':str(OUT)}))
if __name__ == '__main__':
    main()
