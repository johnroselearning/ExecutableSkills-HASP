"""Offline contract; writes NEW pilot1b audit only. Never executes historical actions."""
import hashlib
import json
from pathlib import Path
import unittest
from pilot1b_parser import parse_action, normalize_policy_output
HERE = Path(__file__).resolve().parent

class ParserContract(unittest.TestCase):
    def test_accepted(self):
        obj = '{"action":"D","reason":"compare inputs"}'
        for raw in [obj, ' \n'+obj+'\n ', '```json\n'+obj+'\n```', '```\n'+obj+'\n```', '\n```json\n'+obj+'\n```\n']:
            self.assertEqual(parse_action(raw),'D')

    def test_rejected(self):
        obj = '{"action":"D","reason":"compare inputs"}'
        invalid = ['Here is my answer: '+obj, obj+' More text', obj+'\n'+obj,
                   '```json\n'+obj+'\n```\nAdditional explanation',
                   'Explanation\n```json\n'+obj+'\n```',
                   '```json\n'+obj+'\n```\n```json\n'+obj+'\n```',
                   '```json\n'+obj+'\n', '```python\n'+obj+'\n```',
                   '```json\n'+obj+'\n````', '{"action":"D","reason":}',
                   '{"action":"Z","reason":"x"}', '{"action":"D"}',
                   '{"reason":"x"}', '{"action":"D","reason":null}',
                   '[{"action":"D","reason":"x"}]', 'null', '',
                   '```json\n'+obj+'\n'+obj+'\n```',
                   '```json\n{"action":"D",}\n```']
        for raw in invalid:
            with self.subTest(raw=raw), self.assertRaises((ValueError,TypeError)):
                parse_action(raw)

    def test_all_historical_raw_outputs(self):
        records = [json.loads(line) for line in (HERE/'results/pilot1/calls.jsonl').read_text().splitlines()]
        self.assertEqual(len(records),5)
        audit=[]
        for record in records:
            raw = record['response']['message']['content']
            normalized = normalize_policy_output(raw)
            action = parse_action(raw)
            audit.append({'historical_call_id':record['call_id'], 'raw_text':raw,
                          'normalized_text':normalized,'parsed_action':action,'validation_result':'valid',
                          'historical_action_executed':False,'historical_action_rescored':False})
        self.assertEqual([r['parsed_action'] for r in audit], ['C','A','C','C','C'])
        (HERE/'results/pilot1b/historical_parser_contract.json').write_text(json.dumps(audit,indent=2)+'\n')

if __name__ == '__main__':
    unittest.main()
