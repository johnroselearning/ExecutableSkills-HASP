"""Analyze completed primary competition; coverage annotations are joined only here."""
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import random
import statistics
HERE=Path(__file__).resolve().parent
OUT=HERE/'results/competition_primary'
AN=HERE/'analysis'
ARMS=['A','B','C','D']
SIDS=[f'S{i:02d}' for i in range(1,11)]

def mean(xs):return statistics.mean(xs) if xs else None
def score(r):return r['offline']['chosen']['expected_eliminations_per_cost']
def optimal(r):return r['status']=='valid' and r['offline']['chosen']['rank']==1
def metrics(rows):
    good=[r for r in rows if r['status']=='valid']
    delta=[r['offline']['score_difference'] for r in good]
    return {'n':len(rows),'valid':len(good),'invalid':len(rows)-len(good),
      'optimal_count':sum(optimal(r) for r in rows),
      'optimal_rate_all':mean([int(optimal(r)) for r in rows]),
      'optimal_rate_valid':mean([int(optimal(r)) for r in good]),
      'top2_count':sum(r['offline']['chosen']['rank']<=2 for r in good),
      'top2_rate_all':sum(r['offline']['chosen']['rank']<=2 for r in good)/len(rows) if rows else None,
      'top2_rate_valid':mean([int(r['offline']['chosen']['rank']<=2) for r in good]),
      'mean_score':mean([score(r) for r in good]),
      'equal_snapshot_mean_score':mean([mean([score(r) for r in good if r['snapshot']==sid]) for sid in sorted({r['snapshot'] for r in good})]),
      'equal_snapshot_mean_cost':mean([mean([r['offline']['chosen']['cost'] for r in good if r['snapshot']==sid]) for sid in sorted({r['snapshot'] for r in good})]),
      'mean_cost':mean([r['offline']['chosen']['cost'] for r in good]),
      'improved':sum(d>1e-12 for d in delta),'degraded':sum(d<-1e-12 for d in delta),
      'unchanged_score':sum(abs(d)<=1e-12 for d in delta),
      'equal_score_changed_action':sum(abs(r['offline']['score_difference'])<=1e-12 and r['base_action']!=r['executed_action'] for r in good),
      'action_changed':sum(r['base_action']!=r['executed_action'] for r in good),
      'zero_information':sum(r['offline']['chosen']['non_discriminating'] for r in good),
      'repeated_action':sum(r['offline']['chosen']['repeated'] for r in good),
      'mean_base_final_delta':mean(delta),
      'executed_actions':dict(sorted(Counter(r['executed_action'] for r in good).items())),
      'transitions':dict(sorted(Counter(f"{r['base_action']}->{r['executed_action']}" for r in good).items()))}

def bmetrics(rows):
    selected=[r for r in rows if r['selected_pf_ids'] is not None]
    total_e=sum(r['number_eligible'] for r in selected)
    total_s=sum(r['number_selected'] for r in selected)
    total_hit=sum(len(r['selected_intersect_eligible']) for r in selected)
    return {'selector_trials':len(selected),'eligible_opportunities':total_e,
      'selected_count':total_s,'eligible_selected_count':total_hit,
      'eligible_omitted_count':sum(len(r['eligible_not_selected']) for r in selected),
      'ineligible_selected_count':sum(len(r['selected_but_ineligible']) for r in selected),
      'activated_count':sum(r['number_activated'] for r in selected),
      'any_eligible_selected_trials':sum(bool(r['selected_intersect_eligible']) for r in selected),
      'all_eligible_selected_trials':sum(not r['eligible_not_selected'] for r in selected),
      'omission_trials':sum(bool(r['eligible_not_selected']) for r in selected),
      'ineligible_selection_trials':sum(bool(r['selected_but_ineligible']) for r in selected),
      'no_selection_trials':sum(not r['selected_pf_ids'] for r in selected),
      'multi_selection_trials':sum(r['number_selected']>=2 for r in selected),
      'multi_eligible_selection_trials':sum(len(r['selected_intersect_eligible'])>=2 for r in selected),
      'multi_activation_trials':sum(r['number_activated']>=2 for r in selected),
      'revision_trials':sum(r['revision_text'] is not None for r in selected),
      'nonempty_unparsed_trials':sum(r.get('selector_nonempty_unparsed',False) for r in selected),
      'recall_micro':total_hit/total_e if total_e else None,
      'precision_micro':total_hit/total_s if total_s else None,
      'recall_macro':mean([len(r['selected_intersect_eligible'])/r['number_eligible'] for r in selected]),
      'precision_macro_nonempty':mean([len(r['selected_intersect_eligible'])/r['number_selected'] for r in selected if r['number_selected']]),
      'selected_eligible_activation_rate':sum(r['number_activated'] for r in selected)/total_hit if total_hit else None}

def pct(x):return 'NA' if x is None else f'{100*x:.1f}%'
def num(x):return 'NA' if x is None else f'{x:.3f}'
def metric_table(groups):
    lines=['| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |',
           '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for label,m in groups:
        lines.append(f"| {label} | {m['valid']}/{m['n']} | {m['optimal_count']}/{m['n']} ({pct(m['optimal_rate_all'])}) | {m['top2_count']}/{m['n']} | {num(m['mean_score'])} | {num(m['mean_cost'])} | {m['improved']}/{m['n']} | {m['degraded']}/{m['n']} | {m['equal_score_changed_action']} |")
    return lines

def paired(rows,lhs,rhs):
    index={(r['snapshot'],r['trial'],r['arm']):r for r in rows}
    pairs=[(index[(s,t,lhs)],index[(s,t,rhs)]) for s in SIDS for t in range(1,11)]
    valid=[(a,b) for a,b in pairs if a['status']==b['status']=='valid']
    ds=[score(a)-score(b) for a,b in valid]
    per=[]
    for sid in SIDS:
        ps=[(a,b) for a,b in pairs if a['snapshot']==sid]
        vg=[(a,b) for a,b in ps if a['status']==b['status']=='valid']
        per.append({'snapshot':sid,'optimal_delta':mean([int(optimal(a))-int(optimal(b)) for a,b in ps]),
          'score_delta':mean([score(a)-score(b) for a,b in vg]),
          'cost_delta':mean([a['offline']['chosen']['cost']-b['offline']['chosen']['cost'] for a,b in vg])})
    rng=random.Random(92716);boots={k:[] for k in ['optimal_delta','score_delta','cost_delta']}
    for _ in range(10000):
        sample=[rng.choice(per) for _ in per]
        for k in boots:
            xs=[r[k] for r in sample if r[k] is not None]
            if xs:boots[k].append(mean(xs))
    intervals={}
    for k,xs in boots.items():
        xs.sort();intervals[k]=[xs[int(.025*len(xs))],xs[min(len(xs)-1,int(.975*len(xs)))]] if xs else None
    return {'comparison':f'{lhs}-{rhs}','paired_trials':len(pairs),'valid_pairs':len(valid),
      'mean_score_delta':mean(ds),'wins':sum(d>1e-12 for d in ds),
      'losses':sum(d<-1e-12 for d in ds),'ties':sum(abs(d)<=1e-12 for d in ds),
      'action_disagreements':sum(a['executed_action']!=b['executed_action'] for a,b in valid),
      'optimal_rate_delta':mean([int(optimal(a))-int(optimal(b)) for a,b in pairs]),
      'mean_cost_delta':mean([a['offline']['chosen']['cost']-b['offline']['chosen']['cost'] for a,b in valid]),
      'per_snapshot_differences':per,'snapshot_cluster_bootstrap_95pct':intervals,
      'score_delta_distribution':dict(sorted(Counter(f'{d:.12g}' for d in ds).items()))}

def main():
    completion=json.loads((OUT/'completion.json').read_text());assert completion['status']=='complete'
    rows=[json.loads(x) for x in (OUT/'observations.jsonl').read_text().splitlines()]
    assert len(rows)==400 and len({r['observation_id'] for r in rows})==400
    annotation=json.loads((AN/'pf_action_coverage.json').read_text())
    categories={r['snapshot']:r['classification'] for r in annotation['rows']}
    snapshots=json.loads((HERE/'competition_checkpoint/snapshots.json').read_text())
    posterior={r['snapshot']:','.join(r['viable_worlds_offline']) for r in snapshots}
    for r in rows:r['coverage_category']=categories[r['snapshot']]
    overall={a:metrics([r for r in rows if r['arm']==a]) for a in ARMS}
    by_snapshot={s:{a:metrics([r for r in rows if r['snapshot']==s and r['arm']==a]) for a in ARMS} for s in SIDS}
    by_coverage={c:{a:metrics([r for r in rows if r['coverage_category']==c and r['arm']==a]) for a in ARMS} for c in sorted(set(categories.values()))}
    by_eligible={n:{a:metrics([r for r in rows if r['number_eligible']==n and r['arm']==a]) for a in ARMS} for n in [2,3]}
    by_posterior={p:{a:metrics([r for r in rows if posterior[r['snapshot']]==p and r['arm']==a]) for a in ARMS} for p in sorted(set(posterior.values()))}
    b=[r for r in rows if r['arm']=='B'];bm=bmetrics(b)
    per_pf={}
    for pf in snapshots[0]['gates']:
        per_pf[pf]={'available':len(b),'eligible':sum(pf in r['eligible_pf_ids'] for r in b),
          'selected':sum(pf in (r['selected_pf_ids'] or []) for r in b),
          'eligible_selected':sum(pf in r['selected_intersect_eligible'] for r in b),
          'omitted':sum(pf in r['eligible_not_selected'] for r in b),
          'ineligible_selected':sum(pf in r['selected_but_ineligible'] for r in b),
          'activated':sum(pf in r['activated_pf_ids'] for r in b)}
    cross={}
    for field,fn in [('eligible_selected',lambda r:len(r['selected_intersect_eligible'])),
                     ('activated',lambda r:r['number_activated']),
                     ('number_selected',lambda r:r['number_selected']),
                     ('has_ineligible_selection',lambda r:bool(r['selected_but_ineligible']))]:
        cross[field]={str(k):metrics([r for r in b if fn(r)==k]) for k in sorted({fn(r) for r in b},key=str)}
    paired_results=[paired(rows,a,z) for a,z in [('B','A'),('C','A'),('D','A'),('B','D'),('C','B')]]
    b_cov={c:bmetrics([r for r in b if r['coverage_category']==c]) for c in by_coverage}
    nofeedback_pairs={(r['snapshot'],r['trial']) for r in b if not r['interventions']}
    feedback_groups={label:{a:metrics([r for r in rows if r['arm']==a and (((r['snapshot'],r['trial']) in nofeedback_pairs)==is_no)]) for a in ARMS} for label,is_no in [('B_no_feedback',True),('B_feedback',False)]}
    directions={'A':'tracing','B':'comparison','C':'exception inspection','D':'comparison','E':'dependencies','F':'isolation'}
    direction_counts={a:dict(Counter(directions[r['executed_action']] for r in rows if r['arm']==a and r['status']=='valid')) for a in ARMS}
    summary={'overall':overall,'by_snapshot':by_snapshot,'by_coverage':by_coverage,'by_number_eligible':by_eligible,
      'by_viable_world_set':by_posterior,'native_B_selection':bm,'native_B_per_pf':per_pf,'native_B_coverage':b_cov,
      'native_B_cross_tabs':cross,'paired_comparisons':paired_results,'B_feedback_subsets':feedback_groups,
      'direction_counts':direction_counts,'generation_calls':completion['model_calls']}
    (AN/'competition_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    with (AN/'competition_observations.csv').open('w') as f:
        fields=['snapshot','trial','arm','coverage_category','status','number_eligible','number_selected','number_activated',
          'eligible_pf_ids','selected_pf_ids','selected_intersect_eligible','selected_but_ineligible','eligible_not_selected',
          'pf_order','base_action','revision_action','executed_action','score','cost','optimal','top2','score_difference']
        w=csv.DictWriter(f,fields);w.writeheader()
        for r in rows:
            out={k:r.get(k) for k in fields}
            for k,v in list(out.items()):
                if isinstance(v,list):out[k]=';'.join(v)
            if r['status']=='valid':out.update(score=score(r),cost=r['offline']['chosen']['cost'],optimal=optimal(r),top2=r['offline']['chosen']['rank']<=2,score_difference=r['offline']['score_difference'])
            w.writerow(out)
    lines=['# Primary competition stress-test results','',
      f"Completed 10 snapshots × 10 seeds × A/B/C/D = 400 observations using {completion['model_calls']} generation calls. No reversal conditions, additional samples or proposed selector were run.",'',
      '## Per-snapshot executed-action results','',
      'Optimal and top-2 are rates of the executed action under the unchanged evaluator. Improvement/degradation compare its score with the shared base in the same snapshot. Mean score and cost use valid executions; rates use all planned observations. Exact-action best-strategy alignment equals the optimal rate, not PF selection.','']
    for sid in SIDS:
        s=next(s for s in snapshots if s['snapshot']==sid)
        lines += [f"### {sid} — {categories[sid]}",'',f"Eligible: {', '.join(s['eligible'])}. Offline best: {', '.join(s['best_actions'])}. Viable set: {posterior[sid]} (offline only).",'']
        lines += metric_table([(a,by_snapshot[sid][a]) for a in ARMS])+['']
    lines += ['## Overall primary comparison','']+metric_table(list(overall.items()))+['',
      'Each snapshot has ten trials, so these all-attempt means weight snapshots equally. Valid-execution denominators and all action transitions are included in analysis/competition_summary.json. Invalid executions are not zero-cost or zero-score successes.','',
      '| Arm | Optimal / valid | Top-2 / valid | Zero-information actions | Repeated actions | Executed A–F counts |',
      '|---|---:|---:|---:|---:|---|']
    for a,m in overall.items():lines.append(f"| {a} | {m['optimal_count']}/{m['valid']} | {m['top2_count']}/{m['valid']} | {m['zero_information']} | {m['repeated_action']} | {json.dumps(m['executed_actions'],sort_keys=True)} |")
    lines += ['', '| Arm | Equal-snapshot mean score | Equal-snapshot mean cost |', '|---|---:|---:|']
    for a,m in overall.items():lines.append(f"| {a} | {num(m['equal_snapshot_mean_score'])} | {num(m['equal_snapshot_mean_cost'])} |")
    lines += ['', '## Paired comparisons and uncertainty','',
      'Differences are left minus right within the same snapshot/seed. Win/loss/tie compares executed diagnostic score. Intervals are descriptive percentile 95% intervals from 10,000 resamples of the ten whole snapshot clusters (fixed analysis RNG 92716). These structurally related snapshots are not a random sample of diagnostic problems; intervals do not establish population generality or reliable significance.','',
      '| Pair | Valid pairs | Score wins / losses / ties | Mean score delta [cluster interval] | Optimal-rate delta [cluster interval] | Mean cost delta | Action disagreements |',
      '|---|---:|---:|---|---|---:|---:|']
    for p in paired_results:
        ci=p['snapshot_cluster_bootstrap_95pct']
        lines.append(f"| {p['comparison']} | {p['valid_pairs']} | {p['wins']} / {p['losses']} / {p['ties']} | {num(p['mean_score_delta'])} [{num(ci['score_delta'][0])}, {num(ci['score_delta'][1])}] | {pct(p['optimal_rate_delta'])} [{pct(ci['optimal_delta'][0])}, {pct(ci['optimal_delta'][1])}] | {num(p['mean_cost_delta'])} | {p['action_disagreements']} |")
    lines += ['', '## Coverage annotation strata','',
      'Frozen before inference: five CLEAR_SUPPORT snapshots (S01/S02/S05/S06/S08), three AMBIGUOUS_SUPPORT (S04/S07/S10), two NO_CLEAR_SUPPORT (S03/S09). These are subjective bundle-level interpretation annotations, not randomized groups or a best-PF oracle. They do not contribute to action scoring. Clear states all have D among their best actions; the other states have B as their sole optimum. Coverage is therefore entangled with evidence and optimal-action identity.','']
    for cat,g in by_coverage.items():lines += [f'### {cat}','']+metric_table(list(g.items()))+['']
    lines += ['## Native B: selection → activation → feedback → revision → execution → value','',
      f"Selector trials: {bm['selector_trials']}. At least one eligible PF selected: {bm['any_eligible_selected_trials']}; all eligible selected: {bm['all_eligible_selected_trials']}. Eligible selections: {bm['eligible_selected_count']}/{bm['eligible_opportunities']}; omitted eligible PF opportunities: {bm['eligible_omitted_count']} across {bm['omission_trials']} trials. Ineligible selections: {bm['ineligible_selected_count']}/{bm['selected_count']} across {bm['ineligible_selection_trials']} trials.",'',
      f"Eligible recall: micro {pct(bm['recall_micro'])}, macro {pct(bm['recall_macro'])}. Selection precision: micro {pct(bm['precision_micro'])}, macro over nonempty selections {pct(bm['precision_macro_nonempty'])}. Empty selections: {bm['no_selection_trials']}; nonempty text yielding no parsed IDs: {bm['nonempty_unparsed_trials']}. Empty-set precision remains undefined.",'',
      f"Selected eligible PF activations: {bm['activated_count']}/{bm['eligible_selected_count']} ({pct(bm['selected_eligible_activation_rate'])}). Trials selecting multiple IDs: {bm['multi_selection_trials']}; selecting multiple genuinely eligible IDs: {bm['multi_eligible_selection_trials']}; actually activating multiple PFs: {bm['multi_activation_trials']}. Feedback-triggered policy revisions: {bm['revision_trials']}. These quantities are separate from executed-action success.",'',
      '| PF | Eligible opportunities | Selected | Eligible selected | Eligible omitted | Ineligible selected | Activated |',
      '|---|---:|---:|---:|---:|---:|---:|']
    for pf,m in per_pf.items():lines.append(f"| {pf} | {m['eligible']} | {m['selected']} | {m['eligible_selected']} | {m['omitted']} | {m['ineligible_selected']} | {m['activated']} |")
    lines += ['', 'Exact native feedback strings/order, raw selector responses, revision texts and executed actions are preserved separately in results/competition_primary/observations.jsonl; request/response payloads and token counts are in requests.jsonl and calls.jsonl. Native PF record previews truncate long context_text fields; the separate interventions array preserves full text.','']
    for field,groups in cross.items():lines += [f'### B action quality by {field}','']+metric_table(list(groups.items()))+['']
    lines += ['### Trials where B did or did not produce feedback','',
      'D always has a neutral extra generation; B only revises when feedback exists. These selected subsets are descriptive, not randomized subgroups.','']
    for name,groups in feedback_groups.items():lines += metric_table([(name+'/'+a,m) for a,m in groups.items()])+['']
    lines += ['## Two versus three eligible PFs','',
      'Eligible count is fixed by each snapshot; differences cannot identify a causal effect of more PFs.','']
    for n,g in by_eligible.items():lines+=metric_table([(f'{n} eligible / {a}',m) for a,m in g.items()])+['']
    lines += ['## Viable-world-set strata (offline only)','']
    for p,g in by_posterior.items():lines+=metric_table([(p+' / '+a,m) for a,m in g.items()])+['']
    lines += ['## Action transitions and diagnostic directions','',
      'B and D actions each cost 1; C exception inspection costs 4, E dependency health costs 2, A tracing costs 3, and F isolation costs 5. Direction names alone do not imply value: B and D are both comparisons but frequently have different scores.','',
      '| Arm | Shared-base → executed-action counts | Direction counts |','|---|---|---|']
    for a,m in overall.items():lines.append(f"| {a} | {json.dumps(m['transitions'],sort_keys=True)} | {json.dumps(direction_counts[a],sort_keys=True)} |")
    lines += ['', '## Scope and integrity','',
      'The unchanged gates allow competing guidance but do not guarantee marginal information. No unique correct PF is identifiable from these broad interventions. Useful-omission claims cannot be inferred just from eligibility; C-minus-B measures a bundle contrast, not individual-PF utility. Selection associations and annotation strata are not causal mediation estimates.','',
      'Unresolved comparison-plus-isolation competition is unavailable in this oracle. The ten snapshots cover only three viable-world sets. B_reverse and C_reverse were not run, so menu-order and intervention-order sensitivity remain unmeasured. No sample expansion or new selector was implemented. Neither good nor poor performance establishes novelty.','']
    report='\n'.join(lines)+'\n'
    interpretation=(AN/'competition_interpretation.md').read_text()
    report=report.replace('## Per-snapshot executed-action results',interpretation+'\n## Per-snapshot executed-action results',1)
    report+='\n'+(AN/'competition_integrity_appendix.md').read_text()
    (HERE/'COMPETITION_RESULTS.md').write_text(report)
    print(json.dumps({'overall':overall,'native_B':bm,'paired':[{k:p[k] for k in ['comparison','wins','losses','ties','mean_score_delta','optimal_rate_delta']} for p in paired_results]},indent=2))
if __name__=='__main__':main()
