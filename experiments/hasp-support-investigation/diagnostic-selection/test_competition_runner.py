"""Offline contract tests. Fake outputs only; never contact a model."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
import competition_runner as runner

class FakeModel:
    def __init__(self):self.cache={}
    def generate(self,messages,i,t,role,arm):
        cid=f'{i}-{t}-{role}-{arm}'
        assert cid not in self.cache
        # One invalid base invalidates all four arms; one invalid B revision.
        if role=='policy':text='invalid' if (i,t)==(0,0) else '{"action":"A","reason":"fixture"}'
        elif role=='selector':text='<pf>evidence_collection</pf><pf>binary_isolation</pf>'
        else:text='invalid' if (i,t,arm)==(1,0,'B') else '{"action":"D","reason":"fixture"}'
        result={'call_id':cid,'response':{'message':{'content':text}}};self.cache[cid]=result
        return result

class Contracts(unittest.TestCase):
    def test_full_fake_primary(self):
        original=runner.OUT
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)
            for name in ['annotation_freeze.json','version.json','tags.json','show.json','runtime.log']:
                shutil.copyfile(original/name,target/name)
            shutil.copytree(original/'frozen/analysis',target/'frozen/analysis')
            (target/'context_preflight.json').write_text('[]\n')
            with patch.object(runner,'OUT',target),patch.object(runner,'Model',FakeModel),patch.object(runner,'preflight',return_value=1000),patch.object(sys,'argv',['test','--run-approved-primary']),contextlib.redirect_stdout(io.StringIO()):
                runner.main()
            rows=[json.loads(x) for x in (target/'observations.jsonl').read_text().splitlines()]
            self.assertEqual(len(rows),400)
            self.assertEqual(sum(r['status']=='invalid_base' for r in rows),4)
            self.assertEqual(sum(r['status']=='invalid_final' for r in rows),1)
            for r in rows:
                if r['status']=='invalid_base':continue
                self.assertEqual(r['base_action'],'A')
                self.assertTrue(all(v==0 for v in r['fire_counts_before'].values()))
                if r['arm']=='A':self.assertEqual(r['executed_action'],'A')
                if r['arm']=='C':self.assertEqual(r['activated_pf_ids'],r['eligible_pf_ids'])
                if r['arm']=='D':self.assertFalse(r['interventions']);self.assertIsNotNone(r['revision_text'])
                if r['arm']=='B':
                    self.assertEqual(r['activated_pf_ids'],r['selected_intersect_eligible'])
                    self.assertEqual(set(r['eligible_not_selected']),set(r['eligible_pf_ids'])-set(r['selected_pf_ids']))
            for i in range(1,11):
                for t in range(1,11):
                    quartet=[r for r in rows if r['snapshot']==f'S{i:02d}' and r['trial']==t]
                    self.assertEqual(len({r['calls']['policy'] for r in quartet}),1)
    def test_seed_payload_and_no_annotation(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(runner,'OUT',Path(temp)):
            m=runner.Model.__new__(runner.Model);m.cache={};m.pending={}
            m.check_context=lambda msgs,predict:{'rendered_input_counts':[20,24]}
            seen=[]
            def response(url,payload):
                seen.append(payload)
                return {'message':{'content':'{}'},'prompt_eval_count':20,'eval_count':2}
            with patch.object(runner,'post',side_effect=response):
                for role in ['policy','selector','revision']:
                    m.generate([{'role':'user','content':'fixture'}],2,9,role,'test')
            self.assertEqual([p['options']['seed'] for p in seen],[2110,102110,202110])
            self.assertEqual([p['options']['num_predict'] for p in seen],[256,256,512])
            self.assertTrue(all(p['options']['num_ctx']==4096 and p['think'] is False for p in seen))
if __name__=='__main__':unittest.main()
