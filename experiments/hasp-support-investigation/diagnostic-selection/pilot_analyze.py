"""Read-only Pilot 1 accounting and audit. Does not repair outputs or rerun inference."""
import csv
import hashlib
import json
from pathlib import Path
from statistics import mean
HERE = Path(__file__).resolve().parent
OUT = HERE/'results/pilot1'

def read(name):
    return [json.loads(line) for line in (OUT/name).read_text().splitlines()]

def main():
    manifest = json.loads((OUT/'manifest.json').read_text())
    completion = json.loads((OUT/'completion.json').read_text())
    episodes, steps, calls = read('episodes.jsonl'), read('steps.jsonl'), read('calls.jsonl')
    call_map = {r['call_id']:r for r in calls}
    assert len(episodes)==80 and len({r['episode'] for r in episodes})==80
    # Audit frozen evaluation and execution inputs without changing any source.
    checked = {}
    for path, digest in manifest['source_hashes'].items():
        source = Path(path) if Path(path).is_absolute() else HERE/path
        assert hashlib.sha256(source.read_bytes()).hexdigest()==digest, path
        frozen_name = 'native_'+source.name if Path(path).is_absolute() else source.name
        assert hashlib.sha256((OUT/'frozen'/frozen_name).read_bytes()).hexdigest()==digest, frozen_name
        checked[path] = digest
    for step in steps:
        for call in step['calls'].values():
            assert call in call_map
        assert step['cumulative_evidence']['problem']=='Checkout returns HTTP 500. No root cause is known.'
    # Actual observed Pilot 1 outcome. These checks prevent inadvertently reporting a
    # different/incomplete run as this early-format-failure result.
    assert len(calls)==5 and len(steps)==80
    assert all(r['status']=='invalid_output' and r['steps']==0 and r['cost']==0 for r in episodes)
    assert all(r['failure_stage']=='base_policy' and r['resulting_policy_action'] is None for r in steps)
    assert all(r['selected_pf_ids'] is None and not r['records'] and not r['interventions'] for r in steps)
    assert all(r['role']=='policy' and r['response']['done_reason']=='stop' for r in calls)
    assert all(r['response']['message']['content'].startswith('```json') for r in calls)
    assert len({json.dumps(r['request']['messages'],sort_keys=True) for r in calls})==1
    assert sorted(r['request']['options']['seed'] for r in calls)==[101,102,103,104,105]
    assert all(sum(s['calls']['policy']==c['call_id'] for s in steps)==16 for c in calls)
    for r in calls:
        text=json.dumps(r['request']['messages'])
        assert not any(x in text for x in ['H1','H2','H3','H4','expected_eliminations','viable_before','ground_truth'])
    rows=[]
    for world in manifest['worlds']:
        for arm in manifest['arms']:
            subset=[r for r in episodes if r['world']==world and r['arm']==arm]
            rows.append({'world':world,'arm':arm,'attempted':len(subset),
                         'invalid_outputs':len(subset), 'isolated':0,'isolation_rate_attempted':0,
                         'executed_actions':0,'expected_optimal_action_rate':None,
                         'optimal_decision_yield_including_invalid':0,
                         'mean_cost_spent':0,'mean_executed_steps':0,'steps_to_isolation':None,
                         'zero_information_count':0,'zero_information_rate':None,
                         'redundant_repeat_count':0,'redundant_repeat_rate':None})
    summary={'status':'complete_but_diagnostic_comparison_not_reached',
             'episode_attempts':80,'primary_attempts':60,'order_sensitivity_attempts':20,
             'unique_model_calls':5,'unique_initial_proposals':5,'shared_call_references':75,
             'world_arm_rows':rows,'pf_selector_calls':0,'pf_dispatch_calls':0,'revision_calls':0,
             'executed_diagnostic_actions':0,'input_tokens':sum(r['response']['prompt_eval_count'] for r in calls),
             'output_tokens':sum(r['response']['eval_count'] for r in calls),
             'wall_seconds':completion['wall_seconds'],
             'model_call_wall_seconds':sum(r['wall_seconds'] for r in calls),
             'mean_call_wall_seconds':mean(r['wall_seconds'] for r in calls),
             'api_cost_usd':0,'evaluation_sources_unchanged':True,'audited_hashes':checked,
             'interpretation':'Format failure under frozen bare-JSON contract; native HASP diagnostic performance unmeasured.'}
    (HERE/'analysis/pilot1_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    with (HERE/'analysis/pilot1_by_world_arm.csv').open('w',newline='') as target:
        writer=csv.DictWriter(target,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    trajectories=[]
    for call in calls:
        linked=[s for s in steps if s['calls']['policy']==call['call_id']]
        trajectories.append({'kind':'full_unique_initial_trajectory_with_paired_references',
            'representative_episode':linked[0]['episode'],
            'all_affected_episodes':[r['episode'] for r in linked],
            'request':call['request'],'raw_response':call['response'],
            'trace':linked[0], 'terminal_status':'invalid_output_before_any_action'})
    with (HERE/'traces/pilot1_full_trajectories.jsonl').open('w') as target:
        for trajectory in trajectories: target.write(json.dumps(trajectory)+'\n')
    md=['# Pilot 1 — full representative trajectories','',
        'These are all five unique model calls. Each is referenced by 16 paired episode attempts.',
        'No response has been cleaned, reparsed into an action, or executed.','']
    for trajectory in trajectories:
        md += [f"## {trajectory['representative_episode']}",'',
               'Affected episodes: '+', '.join(trajectory['all_affected_episodes']),'',
               'Full provider request:','', '````json',json.dumps(trajectory['request'],indent=2),'````','',
               'Unmodified response content:','','````text',trajectory['raw_response']['message']['content'],'````','',
               'Provider response and timings:','','````json',json.dumps(trajectory['raw_response'],indent=2),'````','',
               'PF selector: not invoked. Native gates: not evaluated. Interventions: none. '
               'Executed action/observation: none. Cost: 0. Viable worlds remain H1/H2/H3/H4. '
               'Terminal status: invalid_output at base_policy.','']
    (HERE/'analysis/PILOT1_TRAJECTORIES.md').write_text('\n'.join(md)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ['world_arm_rows','audited_hashes']},indent=2))

if __name__=='__main__':
    main()
