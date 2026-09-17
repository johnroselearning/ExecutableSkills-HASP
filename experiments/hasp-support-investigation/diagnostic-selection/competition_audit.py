"""Independent post-run integrity audit; no model calls."""
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
from native_adapter import (IDS,load_native,policy_messages,selector_messages,revision_messages,menu_text)
from pilot1b_parser import parse_action
from competition_checkpoint import NEUTRAL,gates
from evaluator import score_actions
HERE=Path(__file__).resolve().parent
OUT=HERE/'results/competition_primary'

def main():
    completion=json.loads((OUT/'completion.json').read_text())
    assert completion['status']=='complete'
    for name,h in completion['source_hashes'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==h,name
    freeze=json.loads((OUT/'annotation_freeze.json').read_text())
    for name,h in freeze['sha256'].items():
        assert hashlib.sha256((HERE/'analysis'/name).read_bytes()).hexdigest()==h
        assert (HERE/'analysis'/name).read_bytes()==(OUT/'frozen/analysis'/name).read_bytes()
    records=[json.loads(x) for x in (OUT/'observations.jsonl').read_text().splitlines()]
    raw_calls=[json.loads(x) for x in (OUT/'calls.jsonl').read_text().splitlines()]
    requests=[json.loads(x) for x in (OUT/'requests.jsonl').read_text().splitlines()]
    calls={c['call_id']:c for c in raw_calls}
    assert len(records)==400 and len({r['observation_id'] for r in records})==400
    assert len(calls)==len(raw_calls)==len(requests)==completion['model_calls']<=500
    assert all(datetime.fromisoformat(c['timestamp'])>datetime.fromisoformat(freeze['frozen_utc']) for c in raw_calls)
    assert Counter(r['arm'] for r in records)==dict.fromkeys('ABCD',100)
    snapshots={s['snapshot']:s for s in json.loads((HERE/'competition_checkpoint/snapshots.json').read_text())}
    _,lib=load_native();menu=menu_text(lib)
    requests_by_id={r['call_id']:r for r in requests}
    for c in raw_calls:
        assert c['request']==requests_by_id[c['call_id']]['request']
        assert 'error' not in c
        payload=c['request'];role=c['role'];i=int(c['snapshot'][1:])-1;t=c['trial']-1
        assert payload['model']=='gemma4e-64k:latest' and payload['think'] is False and payload['stream'] is False
        expected={'temperature':.7,'top_p':1,'top_k':64,'repeat_penalty':1.0,'num_ctx':4096,'num_thread':8,
                  'seed':{'policy':101,'selector':100101,'revision':200101}[role]+i*1000+t,
                  'num_predict':512 if role=='revision' else 256}
        assert payload['options']==expected
        assert c['response']['prompt_eval_count'] in c['context_preflight']['rendered_input_counts']
        assert c['response']['prompt_eval_count']+c['response']['eval_count']<=4096
        encoded=json.dumps(payload)
        assert not any(x in encoded for x in ['CLEAR_SUPPORT','AMBIGUOUS_SUPPORT','NO_CLEAR_SUPPORT','expected_eliminations','viable_worlds_offline','"rank"'])
    for r in records:
        s=snapshots[r['snapshot']];public=s['public_state'];arm=r['arm']
        assert r['public_state']==public
        assert r['all_pf_gates']==gates(public)==s['gates']
        assert r['fire_counts_before']==dict.fromkeys(IDS,0)
        base=calls[r['calls']['policy']]
        assert base['request']['messages']==policy_messages(public)
        assert base['response']['message']['content']==r['base_proposal_text']
        if r['status']=='invalid_base':continue
        assert parse_action(r['base_proposal_text'])==r['base_action']
        if arm=='A':
            assert r['calls']=={'policy':base['call_id']}
            assert r['executed_action']==r['base_action']
        if arm=='B':
            call=calls[r['calls']['selector']]
            assert call['request']['messages']==selector_messages(public,r['base_proposal_text'],menu)
            assert r['pf_order']==r['selected_pf_ids']
            assert r['activated_pf_ids']==r['selected_intersect_eligible']
            assert ('revision' in r['calls'])==bool(r['interventions'])
        if arm=='C':
            assert r['pf_order']==s['eligible']==r['activated_pf_ids']
            assert r['interventions']==s['deterministic_C_dispatch_audit']['interventions']
            assert 'selector' not in r['calls']
        if arm in ('B','C'):
            expected_counts={pf:int(pf in r['activated_pf_ids']) for pf in IDS}
            assert r['fire_counts_after']==expected_counts
            full={pf:txt for pf,txt in zip(s['eligible'],s['deterministic_C_dispatch_audit']['interventions'],strict=True)}
            assert r['interventions']==[full[pf] for pf in r['activated_pf_ids']]
        if 'revision' in r['calls']:
            c=calls[r['calls']['revision']]
            expected=(policy_messages(public)+[{'role':'assistant','content':r['base_proposal_text']},{'role':'user','content':NEUTRAL}]
                      if arm=='D' else revision_messages(public,r['dispatch_argument'],r['interventions']))
            assert c['request']['messages']==expected
            assert c['response']['message']['content']==r['revision_text']
        if r['status']=='valid':
            text=r['revision_text'] if r['revision_text'] is not None else r['base_proposal_text']
            assert parse_action(text)==r['executed_action']
            scores=score_actions(public['history'],'H1')
            assert scores==r['offline']['all_action_scores']
            assert r['offline']['chosen']==next(s for s in scores if s['action']==r['executed_action'])
    for sid in snapshots:
        for t in range(1,11):
            quartet=[r for r in records if r['snapshot']==sid and r['trial']==t]
            assert len(quartet)==4 and len({r['calls']['policy'] for r in quartet})==1
    stats={'passed':True,'observations':400,'generation_calls':len(raw_calls),
      'role_counts':dict(Counter(c['role'] for c in raw_calls)),
      'status_counts':dict(Counter(r['status'] for r in records)),
      'annotation_frozen_before_all_generations':True,'all_frozen_hashes_match':True,
      'all_prompts_seeds_and_sampling_match':True,'all_scores_recomputed_match':True,
      'all_shared_proposals_match':True,'all_activations_and_full_interventions_match':True,
      'min_prompt_tokens':min(c['response']['prompt_eval_count'] for c in raw_calls),
      'max_prompt_tokens':max(c['response']['prompt_eval_count'] for c in raw_calls),
      'max_total_tokens':max(c['response']['prompt_eval_count']+c['response']['eval_count'] for c in raw_calls),
      'done_reasons':dict(Counter(c['response']['done_reason'] for c in raw_calls)),
      'generation_wall_seconds_sum':sum(c['wall_seconds'] for c in raw_calls)}
    (HERE/'analysis/competition_integrity.json').write_text(json.dumps(stats,indent=2)+'\n')
    print(json.dumps(stats,indent=2))
if __name__=='__main__':main()
