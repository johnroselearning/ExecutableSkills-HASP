"""Checkpoint generator: deterministic CPU work only, no inference entry point."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from actions import ACTIONS
from hypotheses import HYPOTHESES, OUTCOMES
from oracle import CASES, OBSERVATIONS, case_oracle
from evaluator import score_actions, isolation_baseline, viable
from native_adapter import (ROOT, IDS, load_native, menu_text, policy_messages,
                            selector_messages, dispatch, revision_messages)
HERE = Path(__file__).resolve().parent


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def checkpoint():
    execute, library = load_native()
    all_scores, probes, summary = [], [], {}
    matrix = []
    for action, spec in ACTIONS.items():
        for label, (observation, _) in OBSERVATIONS[action].items():
            supports = [h for h in HYPOTHESES if OUTCOMES[action][h] == label]
            matrix.append({'action': action, 'name': spec.name, 'cost': spec.cost,
                           'observation': observation, 'compatible_worlds': supports,
                           'eliminates_from_initial': sorted(set(HYPOTHESES)-set(supports))})
    for case in CASES:
        oracle = case_oracle(case)
        state = oracle.public_state()
        scores = score_actions(state['history'])
        all_scores.extend({'case': case, **row} for row in scores)
        summary[case] = {'history_actions': CASES[case], 'remaining': viable(state['history']),
                         'sunk_cost': sum(r['cost'] for r in state['history']),
                         'best_expected_actions': [r['action'] for r in scores if r['rank']==1],
                         'best_actual_actions': [r['action'] for r in scores if r['actual_eliminations_per_cost']==max(s['actual_eliminations_per_cost'] for s in scores)],
                         **isolation_baseline(state['history'])}
        for order in ('canonical', 'reverse'):
            menu = menu_text(library, order)
            # Explicit mechanical all-retained control, never a simulated selection.
            proposal = '{"action":"A","reason":"Mechanical interface fixture; not a model proposal."}'
            result = dispatch(execute, state, proposal, IDS, {}, 0)
            probes.append({'kind': 'checkpoint_mechanical_all_retained_probe', 'case': case,
                           'order': order, 'cumulative_evidence': state, 'full_pf_menu': menu,
                           'base_model_proposed_action': None, 'fixture_proposal': proposal,
                           'raw_pf_selector_output': None, 'selected_pf_ids': None,
                           'retained_pf_ids': IDS, **result,
                           'resulting_policy_action': None, 'oracle_observation': None,
                           'diagnostic_cost': None,
                           'offline': {'viable_hypotheses': viable(state['history']),
                                       'eliminated_by_executed_action': None},
                           'policy_messages': policy_messages(state),
                           'selector_messages_fixture': selector_messages(state, proposal, menu),
                           'revision_messages_fixture': revision_messages(state, proposal, result['interventions'])})
    matrix_lines = ['# Complete offline evidence matrix', '',
        '**Reviewer-only; never send to the policy or selector.**', '',
        'Compatibility means consistent within these four single-fault worlds, not proof of causality.', '',
        '| Hypothesis | Definition |', '|---|---|']
    matrix_lines += [f'| {h} | {definition} |' for h, definition in HYPOTHESES.items()]
    matrix_lines += ['', '| Action | Cost | Possible observation | Compatible | Eliminates from all four |',
                     '|---|---:|---|---|---|']
    for row in matrix:
        matrix_lines.append(f"| {row['action']} — {row['name']} | {row['cost']} | {row['observation']} | {', '.join(row['compatible_worlds'])} | {', '.join(row['eliminates_from_initial']) or 'none'} |")
    (HERE/'analysis/MATRIX.md').write_text('\n'.join(matrix_lines)+'\n')
    calc = ['# Offline best-next-check calculations', '',
        'Uniform prior conditioned on observed evidence; costs are fixed experimental units.', '',
        '`E[eliminations]/cost = sum(group_size/n * (n-group_size))/cost`', '',
        'Initial partitions: A/E = {H1,H2,H3}|{H4}; B = {H1,H2}|{H3,H4}; '
        'C/D = {H1,H3}|{H2}|{H4}; F = four singletons.', '',
        'For D initially: (2/4 × 2 + 1/4 × 3 + 1/4 × 3)/1 = 2.5. '
        'For B: (2/4 × 2 + 2/4 × 2)/1 = 2.0. '
        'For A: (3/4 × 1 + 1/4 × 3)/3 = 0.5.', '',
        'Entries below are expected eliminations per cost. No scores reach HASP.', '',
        '| Case (prehistory) | Viable | A | B | C | D | E | F | Best | Additional cost lower bound |',
        '|---|---|---:|---:|---:|---:|---:|---:|---|---:|']
    for case, info in summary.items():
        values = [r for r in all_scores if r['case']==case]
        numbers = ' | '.join(f"{r['expected_eliminations_per_cost']:.3f}" for r in values)
        calc.append(f"| {case} ({','.join(CASES[case]) or 'none'}) | {','.join(info['remaining'])} | {numbers} | {','.join(info['best_expected_actions'])} | {info['minimum_additional_cost']} |")
    calc += ['', 'Actual H1 scoring (hindsight sensitivity analysis):', '',
             '| Case | A | B | C | D | E | F | Best actual |', '|---|---:|---:|---:|---:|---:|---:|---|']
    for case, info in summary.items():
        numbers = ' | '.join(f"{r['actual_eliminations_per_cost']:.3f}" for r in all_scores if r['case']==case)
        calc.append(f"| {case} | {numbers} | {','.join(info['best_actual_actions'])} |")
    calc += ['', 'Initial cheapest H1 isolation: B→D or D→B, cost 2 and 2 checks. '
             'Fewest checks: F alone, cost 5 and 1 check. These are different objectives.', '',
             'After D the survivors are H1/H3: B scores 1; F scores 0.2; all other checks score 0. '
             'After B the survivors are H1/H2: D scores 1, C 0.25, F 0.2; all others score 0.', '',
             'After A the survivors are H1/H2/H3: B and D tie at 4/3; F scores 0.4. '
             'B and D occupy both top-2 slots. The evaluator gives F rank 3, not 2.', '',
             'Full observation probabilities, eliminated sets and flags are in action_scores.json; '
             'the CSV contains the scalar metrics. Isolation bounds exclude sunk prehistory cost.']
    (HERE/'analysis/CALCULATIONS.md').write_text('\n'.join(calc)+'\n')
    write_json(HERE/'analysis/evidence_matrix.json', matrix)
    write_json(HERE/'analysis/action_scores.json', all_scores)
    write_json(HERE/'analysis/checkpoint_summary.json', summary)
    with (HERE/'analysis/action_scores.csv').open('w', newline='') as target:
        fields = ['case','action','cost','expected_eliminations','expected_eliminations_per_cost',
                  'actual_eliminations_per_cost','rank','non_discriminating','repeated']
        writer = csv.DictWriter(target, fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(all_scores)
    with (HERE/'traces/checkpoint_mechanical.jsonl').open('w') as target:
        for probe in probes:
            target.write(json.dumps(probe)+'\n')
    paths = list(HERE.glob('*.py')) + [ROOT/'pf_select/pf_select_eval.py',
             ROOT/'skills/executable/support/skills.py', ROOT/'skills/pf_template.py',
             ROOT/'src/skills_agent/skills/program_functions.py']
    paths.extend((ROOT/'skills/executable/docs/support').rglob('*.md'))
    write_json(HERE/'results/checkpoint_manifest.json', {
        'status': 'CHECKPOINT_ONLY_NO_MODEL_RUNS', 'ground_truth_host_only': 'H1',
        'model_trials': 0, 'inference_calls': 0, 'native_pf_changes': 0,
        'files_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)},
        'planned': {'model': 'unselected', 'temperature': 0.7, 'seed_base': 101,
                    'trials_per_cell': 30, 'pilot_trials_per_cell': 10,
                    'max_steps': 8, 'orders': ['canonical','reverse']}})
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkpoint', required=True, action='store_true')
    parser.parse_args()
    checkpoint()
