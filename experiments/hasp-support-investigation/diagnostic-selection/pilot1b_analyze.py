"""Post-hoc accounting only; frozen evaluator remains the sole action scorer."""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
from statistics import mean, median
from actions import ACTIONS
from evaluator import score_actions, viable
from hypotheses import HYPOTHESES
from native_adapter import IDS, policy_messages, selector_messages, revision_messages, load_native, menu_text
from pilot1b_parser import parse_action
HERE = Path(__file__).resolve().parent
OUT = HERE/'results/pilot1b'
ARMS = ['A','B','C','B_reverse']


def read(name):
    return [json.loads(line) for line in (OUT/name).read_text().splitlines()]


def ratio(a,b):
    return a/b if b else None


def percent(value):
    return 'N/A' if value is None else f'{100*value:.1f}%'


def stat(values, fn=mean):
    return fn(values) if values else None


def number(value):
    return 'N/A' if value is None else f'{value:.2f}'


def counter_text(values):
    return ', '.join(f'{k}:{v}' for k,v in sorted(Counter(values).items())) or 'none'


def csv_write(name, rows):
    with (HERE/'analysis'/name).open('w',newline='') as target:
        writer=csv.DictWriter(target,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)


def main():
    manifest=json.loads((OUT/'manifest.json').read_text())
    completion=json.loads((OUT/'completion.json').read_text())
    episodes,steps,calls=read('episodes.jsonl'),read('steps.jsonl'),read('calls.jsonl')
    assert len(episodes)==80 and len({e['episode'] for e in episodes})==80
    preserved=json.loads((OUT/'preexisting_artifact_hashes.json').read_text())
    for name,digest in preserved.items():
        assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==digest, f'Historical artifact changed: {name}'
    for name,digest in manifest['source_hashes'].items():
        source=Path(name) if Path(name).is_absolute() else HERE/name
        assert hashlib.sha256(source.read_bytes()).hexdigest()==digest, f'Frozen source changed: {name}'
        frozen=OUT/'frozen'/source.relative_to(HERE.parents[2])
        assert hashlib.sha256(frozen.read_bytes()).hexdigest()==digest
    call_map={r['call_id']:r for r in calls}
    assert len(calls)==completion['model_calls']
    _,library=load_native()
    enriched=[]
    for s in steps:
        s=dict(s)
        base_call=call_map[s['calls']['policy']]
        assert base_call['request']['messages']==policy_messages(s['cumulative_evidence'])
        if s['raw_pf_selector_output'] is not None:
            selection=call_map[s['calls']['selector']]
            assert selection['request']['messages']==selector_messages(s['cumulative_evidence'],s['base_proposal_text'],s['full_pf_menu'])
            assert s['full_pf_menu']==menu_text(library,'reverse' if s['arm']=='B_reverse' else 'canonical')
        if 'revision' in s['calls']:
            revision=call_map[s['calls']['revision']]
            assert revision['request']['messages']==revision_messages(s['cumulative_evidence'],s['dispatch_argument'],s['interventions'])
        if s['oracle_observation'] is not None:
            rows=score_actions(s['cumulative_evidence']['history'],s['world'])
            assert rows==s['offline']['all_action_scores']
            chosen=next(r for r in rows if r['action']==s['resulting_policy_action'])
            assert chosen==s['offline']['chosen_score']
            assert s['diagnostic_cost']==ACTIONS[s['resulting_policy_action']].cost
            final_text=s['policy_revision_text'] if s['policy_revision_text'] is not None else s.get('dispatch_argument',s['base_proposal_text'])
            assert parse_action(final_text)==s['resulting_policy_action']
            assert s['world'] in s['offline']['viable_after']
            base=next(r for r in rows if r['action']==s['base_model_proposed_action'])
            delta=chosen['expected_eliminations_per_cost']-base['expected_eliminations_per_cost']
            s['posthoc']={'best_actions':[r['action'] for r in rows if r['rank']==1],
                          'base_score':base['expected_eliminations_per_cost'],
                          'executed_score':chosen['expected_eliminations_per_cost'],
                          'score_delta':delta,
                          'score_change':'improved' if delta>1e-12 else 'worse' if delta< -1e-12 else 'unchanged',
                          'action_changed':s['base_model_proposed_action']!=s['resulting_policy_action']}
        enriched.append(s)
    for e in episodes:
        es=[s for s in enriched if s['episode']==e['episode'] and s['oracle_observation'] is not None]
        assert e['actions']==[s['resulting_policy_action'] for s in es]
        assert e['cost']==sum(s['diagnostic_cost'] for s in es)
        assert e['steps']==len(es)
        if e['status']=='isolated': assert e['final_viable']==[e['world']]
    rows=[]
    for world in [*HYPOTHESES,'ALL']:
        for arm in ARMS:
            es=[e for e in episodes if e['arm']==arm and (world=='ALL' or e['world']==world)]
            ss=[s for s in enriched if s['arm']==arm and (world=='ALL' or s['world']==world)]
            valid=[s for s in ss if s['oracle_observation'] is not None]
            successes=[e for e in es if e['status']=='isolated']
            optimal=sum(s['offline']['expected_optimal'] for s in valid)
            top2=sum(s['offline']['top2'] for s in valid)
            zero=sum(s['offline']['zero_information'] for s in valid)
            repeats=sum(s['offline']['redundant_repeat'] for s in valid)
            rows.append({'world':world,'arm':arm,'episodes':len(es),'decisions':len(ss),'executed':len(valid),
                'execution_validity':ratio(len(valid),len(ss)),
                'first_executed_actions':counter_text(e['actions'][0] if e['actions'] else 'none' for e in es),
                'expected_optimal_count':optimal,'expected_optimal_rate':ratio(optimal,len(valid)),
                'optimal_yield_including_invalid':ratio(optimal,len(ss)),
                'mean_episode_optimal_rate':stat([e['expected_optimal_count']/e['steps'] for e in es if e['steps']]),
                'top2_count':top2,'top2_rate':ratio(top2,len(valid)),
                'isolated':len(successes),'isolation_rate':ratio(len(successes),len(es)),
                'mean_cost_spent':stat([e['cost'] for e in es]),'median_cost_spent':stat([e['cost'] for e in es],median),
                'mean_cost_success':stat([e['cost'] for e in successes]),
                'mean_steps_executed':stat([e['steps'] for e in es]),
                'mean_steps_to_isolation':stat([e['steps'] for e in successes]),
                'zero_information_count':zero,'zero_information_rate':ratio(zero,len(valid)),
                'redundant_repeat_count':repeats,'redundant_repeat_rate':ratio(repeats,len(valid)),
                'f_executions':sum(s['resulting_policy_action']=='F' for s in valid),
                'invalid_episodes':sum(e['status']=='invalid_output' for e in es),
                'runtime_error_episodes':sum(e['status']=='runtime_error' for e in es),
                'capped_episodes':sum(e['status']=='step_cap' for e in es)})
    csv_write('pilot1b_by_world_arm.csv',rows)
    changes=[]
    for world in [*HYPOTHESES,'ALL']:
        for arm in ARMS:
            valid=[s for s in enriched if s['arm']==arm and 'posthoc' in s and (world=='ALL' or s['world']==world)]
            changes.append({'world':world,'arm':arm,'executed':len(valid),
                'action_changed':sum(s['posthoc']['action_changed'] for s in valid),
                'improved':sum(s['posthoc']['score_change']=='improved' for s in valid),
                'unchanged_score':sum(s['posthoc']['score_change']=='unchanged' for s in valid),
                'worse':sum(s['posthoc']['score_change']=='worse' for s in valid),
                'base_log_or_trace':sum(s['base_model_proposed_action'] in ['A','C'] for s in valid),
                'log_trace_to_comparison':sum(s['base_model_proposed_action'] in ['A','C'] and s['resulting_policy_action'] in ['B','D'] for s in valid),
                'transitions':counter_text(s['base_model_proposed_action']+'→'+s['resulting_policy_action'] for s in valid)})
    csv_write('pilot1b_proposal_changes.csv',changes)
    pfs=[]
    for world in [*HYPOTHESES,'ALL']:
        for arm in ['B','C','B_reverse']:
            subset=[s for s in enriched if s['arm']==arm and (world=='ALL' or s['world']==world)]
            selectors=[s for s in subset if s['raw_pf_selector_output'] is not None]
            dispatches=[s for s in subset if 'dispatch_action_type' in s]
            for pf in IDS:
                pfs.append({'world':world,'arm':arm,'pf':pf,'selector_turns':len(selectors),
                    'selected':sum(pf in (s['selected_pf_ids'] or []) for s in selectors) if arm!='C' else None,
                    'selection_rate':ratio(sum(pf in (s['selected_pf_ids'] or []) for s in selectors),len(selectors)) if arm!='C' else None,
                    'retained_dispatches':len(dispatches) if arm=='C' else None,
                    'dispatches':len(dispatches),
                    'gate_true':sum(s['should_activate'].get(pf,False) for s in dispatches),
                    'activated':sum(any(r['skill_id']==pf and r['activated'] for r in s['records']) for s in dispatches),
                    'activation_rate_per_dispatch':ratio(sum(any(r['skill_id']==pf and r['activated'] for r in s['records']) for s in dispatches),len(dispatches))})
    csv_write('pilot1b_pf_frequencies.csv',pfs)
    ordering=[]
    for world in HYPOTHESES:
        for trial in range(1,6):
            b=next(e for e in episodes if e['world']==world and e['trial']==trial and e['arm']=='B')
            r=next(e for e in episodes if e['world']==world and e['trial']==trial and e['arm']=='B_reverse')
            bs=[s for s in enriched if s['episode']==b['episode']]
            rs=[s for s in enriched if s['episode']==r['episode']]
            ordering.append({'world':world,'trial':trial,'B_actions':b['actions'],'reverse_actions':r['actions'],
                'same_first_selection':bs[0]['selected_pf_ids']==rs[0]['selected_pf_ids'],
                'same_first_selection_set':set(bs[0]['selected_pf_ids'] or [])==set(rs[0]['selected_pf_ids'] or []),
                'same_first_action':(b['actions'][:1]==r['actions'][:1]),
                'same_trajectory':b['actions']==r['actions'],'cost_delta_reverse_minus_B':r['cost']-b['cost'],
                'steps_delta_reverse_minus_B':r['steps']-b['steps'],
                'B_status':b['status'],'reverse_status':r['status']})
    csv_write('pilot1b_order_pairs.csv',ordering)
    pf_behavior={}
    for arm in ['B','C','B_reverse']:
        subset=[s for s in enriched if s['arm']==arm]
        selectors=[s for s in subset if s['raw_pf_selector_output'] is not None]
        pf_behavior[arm]={'selector_turns':len(selectors),
            'multiple_selected':sum(len(s['selected_pf_ids'] or [])>1 for s in selectors),
            'empty_selections':sum(not s['selected_pf_ids'] for s in selectors),
            'nonempty_unparsed_selections':sum(s.get('selector_nonempty_unparsed',False) for s in selectors),
            'steps_with_interventions':sum(bool(s['interventions']) for s in subset),
            'revisions':sum('revision' in s['calls'] for s in subset)}
    successes=[c for c in calls if 'response' in c]
    summary={'run_id':'pilot1b','episode_attempts':len(episodes),'primary_attempts':60,
        'sensitivity_attempts':20,'unique_calls':len(calls),'roles':dict(Counter(c['role'] for c in calls)),
        'input_tokens':sum(c['response'].get('prompt_eval_count',0) for c in successes),
        'output_tokens':sum(c['response'].get('eval_count',0) for c in successes),
        'wall_seconds':completion['wall_seconds'],'api_cost_usd':0,
        'statuses':dict(Counter(e['status'] for e in episodes)),
        'truncated_calls':[c['call_id'] for c in successes if c['response'].get('done_reason')=='length'],
        'failures':[s for s in enriched if 'error' in s],
        'per_world_arm':rows,'proposal_changes':changes,'pf_behavior':pf_behavior,
        'pf_frequencies':pfs,'order_pairs':ordering,
        'historical_artifacts_preserved':len(preserved),'source_hashes_unchanged':True}
    (HERE/'analysis/pilot1b_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    with (HERE/'traces/pilot1b_scored_steps.jsonl').open('w') as target:
        for s in enriched: target.write(json.dumps(s)+'\n')
    # All full trajectories are retained, not just favorable hand-picked examples.
    with (HERE/'traces/pilot1b_full_trajectories.jsonl').open('w') as target:
        for e in episodes:
            ss=[s for s in enriched if s['episode']==e['episode']]
            ids=sorted({v for s in ss for v in s['calls'].values()})
            target.write(json.dumps({'episode':e,'steps':ss,'model_calls':[call_map[c] for c in ids]})+'\n')
    lines=['# Pilot 1b tables — generated from preserved traces','',
           'Pooled executed-action denominators; mean episode rates also appear in CSV/JSON.','',
           '| World | Arm | Valid actions / decisions | First executed | Optimal | Top-2 | Isolation | Mean cost spent | Mean steps | Zero-info | Repeats |',
           '|---|---|---|---|---|---|---|---:|---:|---|---|']
    for r in rows:
        lines.append(f"| {r['world']} | {r['arm']} | {r['executed']}/{r['decisions']} | {r['first_executed_actions']} | {r['expected_optimal_count']}/{r['executed']} ({percent(r['expected_optimal_rate'])}) | {r['top2_count']}/{r['executed']} ({percent(r['top2_rate'])}) | {r['isolated']}/{r['episodes']} | {number(r['mean_cost_spent'])} | {number(r['mean_steps_executed'])} | {r['zero_information_count']} | {r['redundant_repeat_count']} |")
    lines += ['', '## Proposal → executed action (descriptive association)', '',
              '| World | Arm | Actions | Changed | Improved score | Equal score | Worse score | Transitions |',
              '|---|---|---:|---:|---:|---:|---:|---|']
    for r in changes:
        lines.append(f"| {r['world']} | {r['arm']} | {r['executed']} | {r['action_changed']} | {r['improved']} | {r['unchanged_score']} | {r['worse']} | {r['transitions']} |")
    lines += ['', '## PF frequency', '',
              'Selection denominator: selector turns. Activation denominator: native dispatch calls, including those where that PF was not selected. C is retained, not model-selected.', '',
              '| World | Arm | PF | Selected / selector turns | Gate true | Activated / dispatches |',
              '|---|---|---|---|---:|---|']
    for r in pfs:
        selection='retained' if r['arm']=='C' else f"{r['selected']}/{r['selector_turns']}"
        lines.append(f"| {r['world']} | {r['arm']} | {r['pf']} | {selection} | {r['gate_true']} | {r['activated']}/{r['dispatches']} |")
    (HERE/'analysis/PILOT1B_TABLES.md').write_text('\n'.join(lines)+'\n')
    # Representative rule set before reviewing results: first trial in every world/arm,
    # plus first worse/improved change and each failure. This includes counterexamples.
    reps=[e['episode'] for e in episodes if e['trial']==1]
    for category in ['improved','worse']:
        match=next((s for s in enriched if s.get('posthoc',{}).get('score_change')==category),None)
        if match: reps.append(match['episode'])
    reps += [e['episode'] for e in episodes if e['status']!='isolated']
    reps=list(dict.fromkeys(reps))
    lines=['# Pilot 1b full representative trajectories','',
           'First trial of every world/arm, first improved/worse score change if not already included, and all unsuccessful episodes. All 80 full trajectories also exist as JSONL.','']
    for episode in reps:
        e=next(e for e in episodes if e['episode']==episode)
        ss=[s for s in enriched if s['episode']==episode]
        lines += [f'## {episode}', '', 'Episode outcome:','','```json',json.dumps(e,indent=2),'```','']
        for s in ss:
            lines += [f"### Decision {s['step']+1}",'',
                      'Complete step record (includes evidence, menu, selected/activated PFs, injections, action and offline scores):',
                      '', '````json',json.dumps(s,indent=2),'````','']
            for role,call_id in s['calls'].items():
                lines += [f'Full {role} request and raw response ({call_id}):','',
                          '````json',json.dumps(call_map[call_id],indent=2),'````','']
    (HERE/'analysis/PILOT1B_TRAJECTORIES.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ['failures','per_world_arm','proposal_changes','pf_frequencies','order_pairs']},indent=2))
    print('\n'.join(lines[:4]))

if __name__=='__main__':
    main()
