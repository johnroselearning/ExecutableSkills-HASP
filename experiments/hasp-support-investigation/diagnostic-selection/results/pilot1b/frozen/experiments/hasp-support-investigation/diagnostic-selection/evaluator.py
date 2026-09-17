"""OFFLINE ONLY. Never import this module into a model's input builder."""
from collections import defaultdict
from itertools import permutations
from actions import ACTIONS
from hypotheses import HYPOTHESES, OUTCOMES
from oracle import OBSERVATIONS


def viable(history):
    remaining = set(HYPOTHESES)
    for record in history:
        remaining = {h for h in remaining if OBSERVATIONS[record['action']][OUTCOMES[record['action']][h]][0] == record['observation']}
    if not remaining:
        raise ValueError('Evidence inconsistent with the closed-world model')
    return sorted(remaining)


def score_actions(history, truth='H1'):
    remaining = viable(history)
    rows = []
    for action, spec in ACTIONS.items():
        groups = defaultdict(list)
        for h in remaining:
            groups[OUTCOMES[action][h]].append(h)
        outcomes = [{'observation': OBSERVATIONS[action][label][0],
                     'survivors': sorted(group), 'eliminated': sorted(set(remaining)-set(group)),
                     'probability': len(group)/len(remaining)} for label, group in groups.items()]
        expected = sum(o['probability']*len(o['eliminated']) for o in outcomes)
        actual = next(o for o in outcomes if truth in o['survivors'])
        rows.append({'action': action, 'cost': spec.cost, 'remaining': remaining,
                     'possible_observations': outcomes, 'expected_eliminations': expected,
                     'expected_eliminations_per_cost': expected/spec.cost,
                     'actual_eliminated': actual['eliminated'],
                     'actual_eliminations_per_cost': len(actual['eliminated'])/spec.cost,
                     'non_discriminating': len(groups) == 1,
                     'repeated': any(r['action']==action for r in history)})
    # Competition ranks: tied best actions occupy the first two slots.
    # Include all ties at the second action cutoff.
    levels = sorted([round(r['expected_eliminations_per_cost'], 12) for r in rows], reverse=True)
    for row in rows:
        row['rank'] = levels.index(round(row['expected_eliminations_per_cost'], 12))+1
    return rows


def isolation_baseline(history, truth='H1'):
    """Enumerate fixed-world paths, offline only. This is an oracle lower bound,
    not a deployable selector or an expected-cost optimal decision tree."""
    remaining = viable(history)
    if len(remaining) == 1:
        return {'minimum_additional_cost': 0, 'minimum_additional_steps': 0, 'cheapest_paths': [[]]}
    solutions = []
    for size in range(1, len(ACTIONS)+1):
        for path in permutations(ACTIONS, size):
            survivors = set(remaining)
            for action in path:
                survivors = {h for h in survivors if OUTCOMES[action][h] == OUTCOMES[action][truth]}
            if len(survivors) == 1:
                solutions.append((sum(ACTIONS[a].cost for a in path), size, path))
    cheapest = min(s[0] for s in solutions)
    return {'minimum_additional_cost': cheapest, 'minimum_additional_steps': min(s[1] for s in solutions),
            'cheapest_paths': [list(s[2]) for s in solutions if s[0] == cheapest]}
