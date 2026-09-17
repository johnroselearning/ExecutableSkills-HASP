"""Offline scoring/denominator checks using synthetic records, not model outputs."""
import unittest
from competition_analyze import metrics,bmetrics,paired

def row(s='S01',t=1,a='B',value=1,rank=1,base=.2,status='valid'):
    return {'snapshot':s,'trial':t,'arm':a,'status':status,'base_action':'F','executed_action':'D',
     'revision_text':'{}','selected_pf_ids':['evidence_collection','binary_isolation'],
     'selected_intersect_eligible':['evidence_collection'],'eligible_not_selected':['dependency_trace'],
     'selected_but_ineligible':['binary_isolation'],'number_selected':2,'number_eligible':2,'number_activated':1,
     'offline':{'score_difference':value-base,'chosen':{'expected_eliminations_per_cost':value,
        'rank':rank,'cost':1,'non_discriminating':value==0,'repeated':False}}}
class AnalyzeTests(unittest.TestCase):
    def test_failures_do_not_improve_cost_or_success(self):
        m=metrics([row(),row(status='invalid_final')])
        self.assertEqual(m['optimal_rate_all'],.5)
        self.assertEqual(m['optimal_rate_valid'],1)
        self.assertEqual(m['mean_cost'],1)
        self.assertEqual(m['valid'],1)
    def test_selection_and_execution_separate(self):
        r=row(value=0,rank=3)
        self.assertEqual(bmetrics([r])['selected_eligible_activation_rate'],1)
        self.assertEqual(bmetrics([r])['precision_micro'],.5)
        self.assertEqual(bmetrics([r])['recall_micro'],.5)
        self.assertEqual(metrics([r])['optimal_count'],0)
        self.assertEqual(metrics([r])['degraded'],1)
    def test_empty_precision(self):
        r=row();r.update(selected_pf_ids=[],selected_intersect_eligible=[],selected_but_ineligible=[],number_selected=0,number_activated=0,revision_text=None)
        m=bmetrics([r]);self.assertEqual(m['recall_micro'],0);self.assertIsNone(m['precision_micro'])
    def test_paired_cluster_units(self):
        rows=[row(s=f'S{i:02d}',t=t,a=a,value=1 if a=='B' else .2,rank=1 if a=='B' else 2)
          for i in range(1,11) for t in range(1,11) for a in ['A','B']]
        m=paired(rows,'B','A')
        self.assertEqual(m['wins'],100)
        self.assertAlmostEqual(m['mean_score_delta'],.8)
        self.assertEqual(m['snapshot_cluster_bootstrap_95pct']['optimal_delta'],[1,1])
if __name__=='__main__':unittest.main()
