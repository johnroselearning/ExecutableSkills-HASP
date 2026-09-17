"""Approved primary competition only. No reversal arms or strategy selector added."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import time
import urllib.request
from native_adapter import (IDS, load_native, policy_messages, selector_messages,
                            revision_messages, menu_text, dispatch, selected_ids)
from pilot1b_parser import parse_action
from oracle import Oracle
from evaluator import score_actions
from competition_checkpoint import NEUTRAL, gates
HERE=Path(__file__).resolve().parent
CHECK=HERE/'competition_checkpoint'
OUT=HERE/'results/competition_primary'
MODEL='gemma4e-64k:latest'
OPTIONS={'temperature':.7,'top_p':1,'top_k':64,'repeat_penalty':1.0,'num_ctx':4096,'num_thread':8}

def stamp():return datetime.now(timezone.utc).isoformat()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def append(name,row):
    with (OUT/name).open('a') as f:
        f.write(json.dumps(row,ensure_ascii=False)+'\n');f.flush()
def readlines(name):
    p=OUT/name
    return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []
def post(url,payload):
    request=urllib.request.Request(url,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(request,timeout=600) as r:return json.load(r)
def verify_sources():
    hashes=json.loads((CHECK/'audit.json').read_text())['source_hashes_verified_against_pilot1b']
    for name,h in hashes.items():
        p=Path(name) if Path(name).is_absolute() else HERE/name
        assert digest(p)==h, name
    freeze=json.loads((OUT/'annotation_freeze.json').read_text())
    for name,h in freeze['sha256'].items():
        assert digest(HERE/'analysis'/name)==h
        assert digest(OUT/'frozen/analysis'/name)==h
    return hashes

def rendered_text(messages,empty_thought=False):
    # Text-only projection of Ollama v0.31.2's Gemma4Renderer. No system/tools/thinking.
    # Source: https://raw.githubusercontent.com/ollama/ollama/v0.31.2/model/renderers/gemma4.go
    text='<bos>'
    for m in messages:
        assert set(m)=={'role','content'} and m['role'] in ('user','assistant')
        content=m['content']
        if m['role']=='assistant':
            content=re.sub(r'<\|channel>.*?<channel\|>','',content,flags=re.S)
            content=content.split('<|channel>')[0]
        content=content.strip()
        role='model' if m['role']=='assistant' else 'user'
        text+=f'<|turn>{role}\n{content}<turn|>\n'
    return text+'<|turn>model\n'+('<|channel>thought\n<channel|>' if empty_thought else '')

class Model:
    def __init__(self):
        self.cache={r['call_id']:r for r in readlines('calls.jsonl')}
        self.pending={r['call_id']:r for r in readlines('requests.jsonl')}
        ports=re.findall(r'starting llama-server.*?--port (\d+)',(OUT/'runtime.log').read_text())
        assert ports, 'Load-only runtime initialization required'
        self.token_url=f'http://127.0.0.1:{ports[-1]}/tokenize'
        self.tokens={}
    def count(self,text):
        if text not in self.tokens:
            self.tokens[text]=len(post(self.token_url,{'content':text,'add_special':False,'parse_special':True})['tokens'])
        return self.tokens[text]
    def check_context(self,messages,predict):
        texts=[rendered_text(messages,variant) for variant in [False,True]]
        counts=[self.count(t) for t in texts]
        assert max(counts)+predict<=4096, f'Context overflow: {counts} + {predict}'
        return {'rendered_input_counts':counts,'reserved_output_tokens':predict,
                'context_limit':4096,'rendered_input_sha256':[hashlib.sha256(t.encode()).hexdigest() for t in texts]}
    def generate(self,messages,i,t,role,arm):
        cid=f'S{i+1:02d}-t{t+1:02d}-{arm}-{role}'
        seed={'policy':101,'selector':100101,'revision':200101}[role]+1000*i+t
        predict=512 if role=='revision' else 256
        payload={'model':MODEL,'messages':messages,'stream':False,'think':False,
                 'options':{**OPTIONS,'seed':seed,'num_predict':predict}}
        if cid in self.cache:
            prior=self.cache[cid];assert prior['request']==payload
            if 'error' in prior:raise RuntimeError('Recorded transport failure; no automatic retry')
            return prior
        assert cid not in self.pending, 'Uncertain prior request: refusing duplicate inference'
        context=self.check_context(messages,predict)
        row={'call_id':cid,'timestamp':stamp(),'role':role,'snapshot':f'S{i+1:02d}',
             'trial':t+1,'arm':arm,'request':payload,'context_preflight':context}
        append('requests.jsonl',row);self.pending[cid]=deepcopy(row)
        start=time.monotonic()
        try:
            raw=post('http://127.0.0.1:11435/api/chat',payload)
            row.update(response=raw,wall_seconds=time.monotonic()-start)
            append('calls.jsonl',row);self.cache[cid]=row
            # Counts from the runtime verify the untruncated actual renderer variant.
            assert raw['prompt_eval_count'] in context['rendered_input_counts'], ('Renderer/token count mismatch',cid,raw['prompt_eval_count'],context)
            assert raw['prompt_eval_count']+raw['eval_count']<=4096
            return row
        except Exception as exc:
            if cid not in self.cache:
                row.update(error=repr(exc),wall_seconds=time.monotonic()-start)
                append('calls.jsonl',row);self.cache[cid]=row
            raise

def preflight(model,snapshots,library):
    checks=[]
    menu=menu_text(library)
    for s in snapshots:
        public=s['public_state'];assert gates(public)==s['gates']
        # Conservative 256-token base proposal reserve: selector repeats its tail,
        # hence reserve 512 on top of the static selector prompt, plus output budget.
        for role,msgs,reserve,predict in [
            ('policy',policy_messages(public),0,256),
            ('selector',selector_messages(public,'',menu),512,256),
            ('C_revision',revision_messages(public,'',s['deterministic_C_dispatch_audit']['interventions']),256,512),
            ('D_revision',policy_messages(public)+[{'role':'assistant','content':''},{'role':'user','content':NEUTRAL}],256,512)]:
            check=model.check_context(msgs,predict+reserve)
            checks.append({'snapshot':s['snapshot'],'role':role,'base_proposal_token_reserve':reserve,**check})
    (OUT/'context_preflight.json').write_text(json.dumps(checks,indent=2)+'\n')
    return max(max(c['rendered_input_counts'])+c['reserved_output_tokens'] for c in checks)

def freeze(sources):
    paths=[Path(n) if Path(n).is_absolute() else HERE/n for n in sources]
    paths += [p for p in CHECK.iterdir() if p.is_file()]
    paths += [HERE/'competition_runner.py',HERE/'competition_checkpoint.py',HERE/'competition_annotate.py',
              OUT/'annotation_freeze.json', OUT/'context_preflight.json', OUT/'version.json',OUT/'tags.json',OUT/'show.json']
    hashes={}
    for p in paths:
        rel=(Path('runtime_inputs')/p.relative_to(OUT) if p.is_relative_to(OUT) else
             p.relative_to(HERE) if p.is_relative_to(HERE) else Path('native')/p.relative_to(HERE.parents[2]))
        dest=OUT/'frozen'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p,dest);hashes[str(p)]=digest(p)
    manifest={'started':stamp(),'status':'running','snapshots':10,'trials':10,'arms':['A','B','C','D'],
              'observations':400,'model':MODEL,'options':OPTIONS,'think':False,
              'source_hashes':hashes,'annotation_frozen_before_inference':True,
              'reversals':False,'generation_ceiling':500}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-approved-primary',action='store_true',required=True)
    args=ap.parse_args()
    sources=verify_sources()
    assert json.loads((OUT/'version.json').read_text())['version']=='0.31.2'
    model_info=next(m for m in json.loads((OUT/'tags.json').read_text())['models'] if m['name']==MODEL)
    assert model_info['digest']=='8f3c23b2ff2b1afd1de03317c0fc3e77a27c31222f67b4418db2bb4191ea06d2'
    assert 'AMD Radeon 780M' in (OUT/'runtime.log').read_text()
    execute,library=load_native();model=Model()
    snapshots=json.loads((CHECK/'snapshots.json').read_text())
    maxbound=preflight(model,snapshots,library)
    if (OUT/'manifest.json').exists():
        manifest=json.loads((OUT/'manifest.json').read_text())
        for name,h in manifest['source_hashes'].items():assert digest(Path(name))==h,name
    else:manifest=freeze(sources)
    print(json.dumps({'preflight':'passed','max_context_bound':maxbound,'time':stamp()}),flush=True)
    done={r['observation_id'] for r in readlines('observations.jsonl')}
    menu=menu_text(library)
    for t in range(10):
        for i,s in enumerate(snapshots):
            base=model.generate(policy_messages(s['public_state']),i,t,'policy','shared')
            rawbase=base['response']['message']['content']
            try:proposed=parse_action(rawbase);base_error=None
            except (ValueError,TypeError) as exc:proposed=None;base_error=repr(exc)
            rotated=['B','C','D'];offset=t%3;order=['A']+rotated[offset:]+rotated[:offset]
            for arm in order:
                oid=f"{s['snapshot']}-t{t+1:02d}-{arm}"
                if oid in done:continue
                row={'observation_id':oid,'snapshot':s['snapshot'],'trial':t+1,'arm':arm,'timestamp':stamp(),
                     'public_state':s['public_state'],'available_pf_ids':IDS,'full_pf_menu':menu,
                     'eligible_pf_ids':s['eligible'],'all_pf_gates':s['gates'],'number_eligible':len(s['eligible']),
                     'selected_pf_ids':None,'retained_pf_ids':[],'selected_intersect_eligible':[],
                     'selected_but_ineligible':[],'eligible_not_selected':[],
                     'number_selected':None,'number_activated':0,'pf_order':[],
                     'records':[],'interventions':[],'activated_pf_ids':[],
                     'fire_counts_before':dict.fromkeys(IDS,0),'fire_counts_after':dict.fromkeys(IDS,0),
                     'base_proposal_text':rawbase,'base_action':proposed,'revision_text':None,
                     'revision_action':None,'executed_action':None,'calls':{'policy':base['call_id']},
                     'raw_selector_output':None,'status':'valid'}
                if base_error:
                    row.update(status='invalid_base',error=base_error)
                    append('observations.jsonl',row);done.add(oid);continue
                final=rawbase
                if arm in ('B','C'):
                    if arm=='B':
                        sel=model.generate(selector_messages(s['public_state'],rawbase,menu),i,t,'selector','B')
                        raw=sel['response']['message']['content'];selected=selected_ids(raw)
                        row.update(raw_selector_output=raw,selected_pf_ids=selected,number_selected=len(selected),
                                   selector_nonempty_unparsed=bool(raw.strip() and not selected))
                        row['calls']['selector']=sel['call_id']
                        row['selected_intersect_eligible']=[p for p in selected if p in s['eligible']]
                        row['selected_but_ineligible']=[p for p in selected if p not in s['eligible']]
                        row['eligible_not_selected']=[p for p in s['eligible'] if p not in selected]
                    else:
                        selected=list(s['eligible']);row['retained_pf_ids']=selected
                    row['pf_order']=selected
                    result=dispatch(execute,s['public_state'],rawbase,selected,dict.fromkeys(IDS,0),0)
                    assert not any('error:' in (r.get('reason') or '') for r in result['records'])
                    assert result['dispatch_action_type']=='INVESTIGATE'
                    row.update(result)
                    row['activated_pf_ids']=[r['skill_id'] for r in result['records'] if r['activated']]
                    row['number_activated']=len(row['activated_pf_ids'])
                    assert row['activated_pf_ids']==[p for p in selected if s['gates'][p]]
                    final=result['dispatch_argument']
                    if result['interventions']:
                        rev=model.generate(revision_messages(s['public_state'],final,result['interventions']),i,t,'revision',arm)
                        final=rev['response']['message']['content'];row['revision_text']=final
                        row['calls']['revision']=rev['call_id']
                elif arm=='D':
                    messages=policy_messages(s['public_state'])+[{'role':'assistant','content':rawbase},{'role':'user','content':NEUTRAL}]
                    rev=model.generate(messages,i,t,'revision','D')
                    final=rev['response']['message']['content'];row['revision_text']=final
                    row['calls']['revision']=rev['call_id']
                try:
                    action=parse_action(final)
                    row['executed_action']=action
                    if row['revision_text'] is not None:row['revision_action']=action
                    oracle=Oracle('H1')
                    for a in s['oracle_history']:oracle.execute(a)
                    assert oracle.public_state()==s['public_state']
                    row['oracle_observation']=oracle.execute(action)
                    scores=score_actions(s['public_state']['history'],'H1')
                    chosen=next(r for r in scores if r['action']==action)
                    bs=next(r for r in scores if r['action']==proposed)
                    row['offline']={'all_action_scores':scores,'chosen':chosen,'base':bs,
                        'best_actions':[r['action'] for r in scores if r['rank']==1],
                        'score_difference':chosen['expected_eliminations_per_cost']-bs['expected_eliminations_per_cost']}
                except (ValueError,TypeError) as exc:row.update(status='invalid_final',error=repr(exc))
                append('observations.jsonl',row);done.add(oid)
            print(json.dumps({'completed_observations':len(done),'pair':f"{s['snapshot']}-t{t+1:02d}",'generation_calls':len(model.cache),'time':stamp()}),flush=True)
    assert len(done)==400
    verify_sources()
    for name,h in manifest['source_hashes'].items():assert digest(Path(name))==h,name
    manifest.update(status='complete',completed=stamp(),model_calls=len(model.cache),completed_observations=len(done))
    (OUT/'completion.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'complete':True,'observations':400,'generation_calls':len(model.cache)}),flush=True)
if __name__=='__main__':main()
