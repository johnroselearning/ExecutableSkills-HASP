"""Meaningful environment invariants and native adapter contract checks; no model calls."""
import itertools
import json
import unittest
from actions import ACTIONS
from hypotheses import HYPOTHESES
from oracle import Oracle, CASES, case_oracle
from evaluator import viable, score_actions, isolation_baseline
from native_adapter import (load_native, menu_text, selected_ids, dispatch, policy_messages, parse_action, IDS)

class DiagnosticTests(unittest.TestCase):
    def test_every_world_every_action_sequence(self):
        for truth in HYPOTHESES:
            for path in itertools.permutations(ACTIONS):
                oracle = Oracle(truth)
                remaining = set(HYPOTHESES)
                for action in path:
                    oracle.execute(action)
                    new = set(viable(oracle.public_state()['history']))
                    self.assertIn(truth, new)
                    self.assertLessEqual(new, remaining)
                    remaining = new
                self.assertEqual(remaining, {truth})

    def test_repeats_and_copies(self):
        oracle = Oracle()
        a = oracle.execute('D')
        self.assertEqual(a, oracle.execute('D'))
        a['facts']['differing_headers'].append('poison')
        self.assertNotIn('poison', oracle.public_state()['support_evidence']['differing_headers'])
        row = next(r for r in score_actions(oracle.public_state()['history']) if r['action']=='D')
        self.assertTrue(row['non_discriminating'])
        self.assertEqual(row['expected_eliminations'], 0)
        with self.assertRaises(ValueError):
            oracle.execute('unknown')

    def test_hand_calculated_scores(self):
        rows = {r['action']: r for r in score_actions([])}
        self.assertEqual(rows['D']['expected_eliminations_per_cost'], 2.5)
        self.assertEqual(rows['B']['expected_eliminations_per_cost'], 2)
        self.assertEqual(rows['A']['expected_eliminations_per_cost'], .5)
        self.assertEqual(rows['D']['actual_eliminations_per_cost'], 2)
        self.assertEqual(isolation_baseline([])['minimum_additional_cost'], 2)
        self.assertEqual(isolation_baseline([])['minimum_additional_steps'], 1)
        for case in CASES:
            for row in score_actions(case_oracle(case).public_state()['history']):
                self.assertAlmostEqual(sum(o['probability'] for o in row['possible_observations']), 1)

    def test_native_competition_and_fire_caps(self):
        execute, library = load_native()
        normal = menu_text(library)
        self.assertEqual(menu_text(library, 'reverse').splitlines(), normal.splitlines()[::-1])
        self.assertEqual(selected_ids('<pf>comparison_experiment</pf><pf>bogus</pf><pf>comparison_experiment</pf>'), ['comparison_experiment'])
        counts = {}
        state = case_oracle('matched_and_healthy').public_state()
        result = dispatch(execute, state, 'fixture', IDS, counts, 0)
        self.assertGreaterEqual(sum(result['should_activate'].values()), 3)
        again = dispatch(execute, state, 'fixture', IDS, counts, 1)
        self.assertFalse(any(again['should_activate'].values()))
        self.assertFalse(any('error:' in (r.get('reason') or '') for r in result['records']))

    def test_no_host_fields_in_model_input(self):
        state = case_oracle('initial').public_state()
        state.update(ground_truth='SECRET_TRUTH', offline={'rank': 'SECRET_RANK'})
        text = json.dumps(policy_messages(state))
        self.assertNotIn('SECRET', text)
        self.assertNotIn('H1', text)
        self.assertEqual(state['history'], [])
        self.assertEqual(parse_action('{"action":"B","reason":"compare clients"}'), 'B')
        for invalid in ['A', '{"action":"Z","reason":"x"}', '[]']:
            with self.assertRaises((ValueError, TypeError)):
                parse_action(invalid)

if __name__ == '__main__':
    unittest.main()
