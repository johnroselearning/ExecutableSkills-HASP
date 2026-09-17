"""Native prompt/menu/parser/dispatch adapter. No oracle or evaluator imports.
No provider client: live experiments are deliberately unavailable at checkpoint.
"""
import json
from pathlib import Path
import sys
from actions import public_actions
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from pf_select.pf_select_eval import (_load_pf_system, _build_pf_menu,
                                     _parse_pf_selection, _PF_SELECT_INSTRUCTION_TMPL)
IDS = ['evidence_collection', 'request_id_trace', 'comparison_experiment',
       'dependency_trace', 'binary_isolation']


def load_native():
    execute, library = _load_pf_system(str(ROOT / 'skills'))
    from src.skills_agent.skills.program_functions import get_program_function
    assert all(sid in library and get_program_function(sid) for sid in IDS)
    return execute, {sid: library[sid] for sid in IDS}


def menu_text(library, order='canonical'):
    lines = _build_pf_menu(library).splitlines()
    if order == 'reverse':
        lines.reverse()  # Native builder sorts keys; reverse rendered lines explicitly.
    elif order != 'canonical':
        raise ValueError(order)
    return '\n'.join(lines)


def policy_messages(public_state):
    # Explicit projection: do not serialize arbitrary host/evaluator fields.
    history = [{k: r[k] for k in ('action', 'observation', 'cost')}
               for r in public_state['history']]
    problem = {'problem': public_state['problem'], 'observed_history': history,
               'available_actions': public_actions()}
    return [{'role': 'user', 'content': json.dumps(problem, sort_keys=True) +
             '\nChoose the next diagnostic check. Return exactly one JSON object '
             'with keys action (one of A,B,C,D,E,F) and reason (brief text).'}]


def selector_messages(public_state, proposal, menu):
    return policy_messages(public_state) + [
        {'role': 'assistant', 'content': proposal},
        {'role': 'user', 'content': _PF_SELECT_INSTRUCTION_TMPL.format(menu=menu, candidate=proposal[-1200:])}]


def parse_action(raw):
    result = json.loads(raw)
    if not isinstance(result, dict) or result.get('action') not in public_actions() or not isinstance(result.get('reason'), str):
        raise ValueError('Invalid policy action; no fallback action is chosen')
    return result['action']


def dispatch(execute, public_state, proposal, selected, counts, step):
    context = {'question': public_state['problem'], 'domain': 'support',
               'support_evidence': public_state['support_evidence'],
               'evidence': '\n'.join(r['observation'] for r in public_state['history']),
               'raw_reasoning': proposal, 'action_history': public_state['history'],
               'step_count': step, 'max_steps': 8, '_pf_fire_counts': counts}
    from src.skills_agent.skills.program_functions import get_program_function
    # These are the actual native wrapper gates, including native fire caps.
    gates = {sid: bool(get_program_function(sid).should_activate(dict(context), 'INVESTIGATE', proposal))
             for sid in selected}
    before = dict(counts)
    action, argument, records, interventions = execute(
        active_skill_ids=selected, step_context=context,
        action_type='INVESTIGATE', arg=proposal, reasoning=proposal, teacher_model=None)
    return {'should_activate': gates, 'dispatch_action_type': action,
            'dispatch_argument': argument, 'records': [r.to_dict() for r in records],
            'interventions': interventions, 'fire_counts_before': before,
            'fire_counts_after': dict(counts)}


def revision_messages(public_state, proposal, interventions):
    return policy_messages(public_state) + [
        {'role': 'assistant', 'content': proposal},
        {'role': 'user', 'content': '[System Feedback]\n' + '\n\n'.join(interventions) +
         '\n\nPlease provide a revised answer. Use the same single-action JSON format.'}]

# The runner may call this ONLY after a real selector response in condition B.
def selected_ids(raw):
    return _parse_pf_selection(raw, set(IDS))
