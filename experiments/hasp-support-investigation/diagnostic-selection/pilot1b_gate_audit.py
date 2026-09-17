"""Offline coverage audit; never dispatches PFs, executes actions or calls a model."""
import json
from pathlib import Path
from native_adapter import load_native, IDS
HERE=Path(__file__).resolve().parent

def main():
    load_native()
    from src.skills_agent.skills.program_functions import get_program_function
    steps=[json.loads(line) for line in (HERE/'results/pilot1b/steps.jsonl').read_text().splitlines()]
    rows=[]
    for r in steps:
        if r['base_model_proposed_action'] is None:
            continue
        ctx={'question':r['cumulative_evidence']['problem'],'domain':'support',
             'support_evidence':r['cumulative_evidence']['support_evidence'],
             '_pf_fire_counts':dict(r['fire_counts_before']), 'step_count':r['step'],'max_steps':8}
        gates={pf:bool(get_program_function(pf).should_activate(dict(ctx),'INVESTIGATE',r['base_proposal_text'])) for pf in IDS}
        # This second pass is explicitly a counterfactual prerequisite-only audit,
        # not a replacement for the actual gates and never used by the policy.
        uncapped=dict(ctx);uncapped['_pf_fire_counts']={}
        prerequisites={pf:bool(get_program_function(pf).should_activate(dict(uncapped),'INVESTIGATE',r['base_proposal_text'])) for pf in IDS}
        rows.append({'episode':r['episode'],'arm':r['arm'],'world':r['world'],'step':r['step'],
            'offline_all_candidate_gates_at_recorded_counts':gates,
            'offline_prerequisite_gates_without_fire_cap':prerequisites,
            'eligible_competition':sum(gates.values())>1,'prerequisite_overlap':sum(prerequisites.values())>1})
    (HERE/'analysis/pilot1b_gate_coverage.json').write_text(json.dumps(rows,indent=2)+'\n')
    for arm in ['A','B','C','B_reverse']:
        rs=[r for r in rows if r['arm']==arm]
        print(arm, len(rs), 'multiple eligible',sum(r['eligible_competition'] for r in rs),
              'prerequisite overlap ignoring cap',sum(r['prerequisite_overlap'] for r in rs))

if __name__=='__main__': main()
