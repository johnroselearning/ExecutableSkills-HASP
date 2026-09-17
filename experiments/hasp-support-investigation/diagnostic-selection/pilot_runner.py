"""Approved Pilot 1 only. Local inference adapter around frozen native HASP primitives."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import time
import urllib.request
from oracle import Oracle
from hypotheses import HYPOTHESES
from evaluator import viable, score_actions, isolation_baseline
from native_adapter import (IDS, load_native, menu_text, policy_messages, selector_messages,
                            revision_messages, parse_action, selected_ids, dispatch)
HERE = Path(__file__).resolve().parent
OUT = HERE/'results/pilot1'
MODEL = 'gemma4e-64k:latest'
OPTIONS = {'temperature': .7, 'top_p': 1, 'top_k': 64, 'repeat_penalty': 1.0,
           'num_ctx': 4096, 'num_thread': 8}
ARMS = ['A', 'B', 'C', 'B_reverse']


def stamp():
    return datetime.now(timezone.utc).isoformat()


def append(name, record):
    with (OUT/name).open('a') as target:
        target.write(json.dumps(record, ensure_ascii=False)+'\n')
        target.flush()


def seed_for(trial, step, role):
    return 101 + trial + step*1000 + {'policy': 0, 'selector': 100000, 'revision': 200000}[role]


class LocalModel:
    def __init__(self):
        self.count = 0

    def generate(self, messages, trial, step, role, episode):
        self.count += 1
        call_id = f'call-{self.count:05d}'
        payload = {'model': MODEL, 'messages': messages, 'stream': False, 'think': False,
                   'options': {**OPTIONS, 'seed': seed_for(trial, step, role),
                               'num_predict': 512 if role=='revision' else 256}}
        record = {'call_id': call_id, 'episode': episode, 'role': role,
                  'timestamp': stamp(), 'request': payload}
        append('requests.jsonl', record)  # Durable before sending.
        start = time.monotonic()
        try:
            request = urllib.request.Request('http://127.0.0.1:11435/api/chat',
                       data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(request, timeout=600) as response:
                raw = json.load(response)
            record.update(response=raw, wall_seconds=time.monotonic()-start)
            append('calls.jsonl', record)
            return {'call_id': call_id, 'text': raw['message']['content'],
                    'done_reason': raw.get('done_reason')}
        except Exception as exc:
            record.update(error=repr(exc), wall_seconds=time.monotonic()-start)
            append('calls.jsonl', record)
            raise


def run_episode(model, execute, library, truth, trial, arm, initial_cache):
    episode = f'{truth}-t{trial+1}-{arm}'
    oracle, counts = Oracle(truth), {}
    steps = []
    status = 'step_cap'
    menu = menu_text(library, 'reverse' if arm=='B_reverse' else 'canonical')
    for step in range(8):
        public = oracle.public_state()
        record = {'episode': episode, 'world': truth, 'trial': trial+1, 'arm': arm,
                  'step': step, 'cumulative_evidence': public,
                  'full_pf_menu': menu if arm.startswith('B') else None,
                  'available_pf_menu': menu, 'raw_pf_selector_output': None,
                  'selected_pf_ids': None, 'retained_pf_ids': IDS if arm=='C' else [],
                  'should_activate': {}, 'records': [], 'interventions': [],
                  'base_model_proposed_action': None, 'base_proposal_text': None,
                  'policy_revision_text': None, 'resulting_policy_action': None,
                  'oracle_observation': None, 'diagnostic_cost': 0,
                  'fire_counts_before': dict(counts), 'fire_counts_after': dict(counts),
                  'calls': {}, 'timestamp': stamp()}
        try:
            if step == 0 and trial in initial_cache:
                base = initial_cache[trial]
                record['base_proposal_reused'] = True
            else:
                base = model.generate(policy_messages(public), trial, step, 'policy', episode)
                record['base_proposal_reused'] = False
                if step == 0:
                    initial_cache[trial] = base
            record['calls']['policy'] = base['call_id']
            record['base_proposal_text'] = base['text']
            try:
                proposed = parse_action(base['text'])
            except (ValueError, TypeError) as exc:
                record['failure_stage'] = 'base_policy'
                raise ValueError('Invalid base policy output') from exc
            record['base_model_proposed_action'] = proposed
            final = base['text']
            if arm != 'A':
                if arm == 'C':
                    selected = list(IDS)
                else:
                    selection = model.generate(selector_messages(public, final, menu), trial, step, 'selector', episode)
                    record['calls']['selector'] = selection['call_id']
                    record['raw_pf_selector_output'] = selection['text']
                    selected = selected_ids(selection['text'])
                    record['selected_pf_ids'] = selected
                    record['selector_nonempty_unparsed'] = bool(selection['text'].strip() and not selected)
                result = dispatch(execute, public, final, selected, counts, step)
                record.update(result)
                if any('error:' in (r.get('reason') or '') for r in result['records']):
                    raise RuntimeError('Native dispatch error recorded')
                if result['dispatch_action_type'] != 'INVESTIGATE':
                    raise RuntimeError('Unexpected native action type; refusing unreviewed mapping')
                final = result['dispatch_argument']
                if result['interventions']:
                    revision = model.generate(revision_messages(public, final, result['interventions']), trial, step, 'revision', episode)
                    record['calls']['revision'] = revision['call_id']
                    record['policy_revision_text'] = revision['text']
                    final = revision['text']
            try:
                action = parse_action(final)
            except (ValueError, TypeError) as exc:
                record['failure_stage'] = 'revised_policy'
                raise ValueError('Invalid executed policy output') from exc
            record['resulting_policy_action'] = action
            observation = oracle.execute(action)
            # Scores are attached AFTER policy/action selection, and never serialized into public inputs.
            scores = score_actions(public['history'], truth)
            chosen = next(row for row in scores if row['action']==action)
            remaining = viable(oracle.public_state()['history'])
            record.update(oracle_observation=observation, diagnostic_cost=observation['cost'],
                offline={'viable_before': viable(public['history']), 'viable_after': remaining,
                         'all_action_scores': scores, 'chosen_score': chosen,
                         'hypotheses_eliminated': chosen['actual_eliminated'],
                         'expected_optimal': chosen['rank']==1, 'top2': chosen['rank']<=2,
                         'zero_information': chosen['non_discriminating'],
                         'redundant_repeat': chosen['repeated'] and chosen['non_discriminating']})
            if len(remaining)==1:
                status = 'isolated'
        except ValueError as exc:
            status = 'invalid_output'
            record['error'] = repr(exc)
        except Exception as exc:
            status = 'runtime_error'
            record['error'] = repr(exc)
        if 'offline' not in record:
            record['offline'] = {'viable_before': viable(public['history']),
                                 'viable_after': viable(oracle.public_state()['history']),
                                 'hypotheses_eliminated': []}
        record['status_after_step'] = status if status != 'step_cap' else 'continuing'
        append('steps.jsonl', record)
        steps.append(record)
        if status != 'step_cap':
            break
    executed = [r for r in steps if r['oracle_observation'] is not None]
    summary = {'episode': episode, 'world': truth, 'trial': trial+1, 'arm': arm,
               'status': status, 'steps': len(executed), 'cost': sum(r['diagnostic_cost'] for r in executed),
               'actions': [r['resulting_policy_action'] for r in executed],
               'expected_optimal_count': sum(r['offline']['expected_optimal'] for r in executed),
               'top2_count': sum(r['offline']['top2'] for r in executed),
               'zero_information_count': sum(r['offline']['zero_information'] for r in executed),
               'redundant_repeat_count': sum(r['offline']['redundant_repeat'] for r in executed),
               'final_viable': viable(oracle.public_state()['history']),
               'baseline': isolation_baseline([], truth), 'timestamp': stamp()}
    append('episodes.jsonl', summary)
    print(json.dumps({k:summary[k] for k in ['episode','status','actions','cost']}), flush=True)


def freeze():
    OUT.mkdir(exist_ok=True)
    if (OUT/'manifest.json').exists():
        raise SystemExit('Existing run preserved. Refusing rerun/overwrite.')
    paths = [HERE/p for p in ['evaluator.py','hypotheses.py','oracle.py','actions.py',
             'native_adapter.py','pilot_runner.py','PILOT1_PROTOCOL.md']]
    hashes = {}
    for p in paths:
        shutil.copyfile(p, OUT/'frozen'/p.name)
        hashes[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    native_paths = [HERE.parents[2]/p for p in ['pf_select/pf_select_eval.py',
                    'skills/executable/support/skills.py', 'skills/pf_template.py',
                    'src/skills_agent/skills/program_functions.py']]
    for p in native_paths:
        shutil.copyfile(p, OUT/'frozen'/('native_'+p.name))
        hashes[str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()
    manifest = {'run_id':'pilot1', 'started':stamp(), 'status':'running', 'worlds':list(HYPOTHESES),
                'trials':5, 'arms':ARMS, 'episodes':80, 'initial_case':'initial', 'max_steps':8,
                'model':MODEL, 'options':OPTIONS, 'think':False, 'source_hashes':hashes,
                'selector':'native pf_select_eval unchanged prompt/parser',
                'rendered_provider_prompt':'Not exposed by Ollama; exact messages plus saved /api/show template available.'}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-approved-pilot1', required=True, action='store_true')
    parser.parse_args()
    manifest = freeze()
    execute, library = load_native()
    model, initial_cache = LocalModel(), {}
    started = time.monotonic()
    worlds = list(HYPOTHESES)
    for trial in range(5):
        for truth in worlds[trial%4:]+worlds[:trial%4]:
            for arm in ARMS[trial%4:]+ARMS[:trial%4]:
                run_episode(model, execute, library, truth, trial, arm, initial_cache)
    manifest.update(status='complete', completed=stamp(), model_calls=model.count,
                    wall_seconds=time.monotonic()-started)
    (OUT/'completion.json').write_text(json.dumps(manifest,indent=2)+'\n')

if __name__ == '__main__':
    main()
