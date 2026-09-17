"""Interpretation-only pre-inference bundle annotation; never imported by policy code."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from native_adapter import IDS, load_native, dispatch
HERE=Path(__file__).resolve().parent
OUT=HERE/'analysis'
REASONS={
'S01':('CLEAR_SUPPORT','The missing-evidence intervention explicitly asks to capture request headers and body, which naturally supports D. No claim is made that it specifically endorses both tied best actions B and D.'),
'S02':('CLEAR_SUPPORT','The bundle explicitly asks to compare failing web and successful mobile request headers and payloads, naturally supporting D.'),
'S03':('NO_CLEAR_SUPPORT','The bundle asks for request capture, correlated tracing and dependency inspection. None explicitly asks to reproduce on both matched clients, the best action B; capture alone is not that experiment.'),
'S04':('AMBIGUOUS_SUPPORT','Isolation asks for a test reproduction against a known-good control. Establishing a matched mobile control could lead to B, but the intervention does not name that client comparison and instead prescribes bisection. Dependency text mentions mobile success only as a caveat, not an instruction to run B.'),
'S05':('CLEAR_SUPPORT','The missing-evidence intervention explicitly asks for request headers and body capture, naturally supporting tied-best D. The trace guidance does not itself establish best-action support.'),
'S06':('CLEAR_SUPPORT','The comparison intervention explicitly asks to compare matched failing web and successful mobile headers and payloads, naturally supporting D.'),
'S07':('AMBIGUOUS_SUPPORT','Isolation calls for a test reproduction against a known-good control, which could motivate establishing the matched mobile baseline B. It does not explicitly request web/mobile reproduction; bisection and downstream inspection are its direct guidance.'),
'S08':('CLEAR_SUPPORT','The comparison intervention explicitly asks to compare matched failing web and successful mobile request headers and payloads, naturally supporting D.'),
'S09':('NO_CLEAR_SUPPORT','Request capture and correlated tracing do not explicitly direct matched web/mobile reproduction B. The bundle contains no comparison or control-baseline guidance.'),
'S10':('AMBIGUOUS_SUPPORT','The isolation intervention requests a known-good control for test reproduction. This could lead to establishing the matched mobile baseline B, but mobile and the matched-client test are not specified; tracing and bisection are the explicit directions.'),
}
def main():
    target=OUT/'pf_action_coverage.json'
    if target.exists(): raise SystemExit('Refusing to overwrite frozen annotation')
    snapshots=json.loads((HERE/'competition_checkpoint/snapshots.json').read_text())
    execute,_=load_native(); rows=[]
    for s in snapshots:
        audit=dispatch(execute,s['public_state'],'<OFFLINE INTERVENTION AUDIT>',s['eligible'],dict.fromkeys(IDS,0),0)
        activated=[r['skill_id'] for r in audit['records'] if r['activated']]
        texts=dict(zip(activated,audit['interventions'],strict=True))
        assert list(texts)==s['eligible']
        assert list(texts.values())==s['deterministic_C_dispatch_audit']['interventions']
        category,reason=REASONS[s['snapshot']]
        rows.append({'snapshot':s['snapshot'],'eligible_pf_ids':s['eligible'],
          'fire_counts_before':audit['fire_counts_before'],'exact_interventions':texts,
          'offline_best_diagnostic_actions':s['best_actions'], 'classification':category,'reason':reason})
    data={'created_utc':datetime.now(timezone.utc).isoformat(),
     'purpose':'Interpretation-only bundle coverage; not a best-PF oracle, selection target, or success score.',
     'question':'Does at least one eligible PF intervention explicitly provide guidance that could naturally lead to one of the offline-best diagnostic actions?',
     'rubric':{'CLEAR_SUPPORT':'Direct guidance names the best action activity or its defining evidence collection operation.',
               'AMBIGUOUS_SUPPORT':'Guidance could motivate a prerequisite/control leading to the best action, but does not specify that action; inferential bridge required.',
               'NO_CLEAR_SUPPORT':'No explicit best-action activity or natural control-baseline guidance; only a generic possibility that reasoning might reach it.'},
     'rows':rows}
    OUT.mkdir(exist_ok=True)
    target.write_text(json.dumps(data,indent=2)+'\n')
    md=['# PF action coverage — frozen before inference','',data['question'],'',data['purpose'],
        '', 'These are subjective bundle annotations, not PF utility/rank/correctness labels. Clear support does not mean the entire bundle recommends the optimum. Ambiguous support is deliberately a weak reading of known-good-control guidance. Categories are not randomized groups and never enter prompts or optimal-action scoring.','']
    for r in rows:
        md += ['## '+r['snapshot'], '',f"Eligible: {', '.join(r['eligible_pf_ids'])}. All fire counts initially zero.",
               '',f"Offline best: {', '.join(r['offline_best_diagnostic_actions'])}. **{r['classification']}**.",'',r['reason'],'']
        for pf,txt in r['exact_interventions'].items(): md += [f'### {pf}', '',txt,'']
    (OUT/'PF_ACTION_COVERAGE.md').write_text('\n'.join(md)+'\n')
    freeze=HERE/'results/competition_primary/frozen/analysis'
    freeze.mkdir(parents=True,exist_ok=True)
    hashes={}
    for name in ['PF_ACTION_COVERAGE.md','pf_action_coverage.json']:
        b=(OUT/name).read_bytes();(freeze/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest()
    (freeze.parent.parent/'annotation_freeze.json').write_text(json.dumps({'frozen_utc':datetime.now(timezone.utc).isoformat(),'sha256':hashes,'model_calls_before_freeze':0},indent=2)+'\n')
    print(json.dumps({'categories':{k:sum(r['classification']==k for r in rows) for k in data['rubric']},'sha256':hashes},indent=2))
if __name__=='__main__':main()
