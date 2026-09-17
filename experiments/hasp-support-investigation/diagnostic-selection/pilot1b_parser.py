"""Interface normalization only: whole-output JSON fence or bare JSON.
No extraction, repair, inference, retry, fallback or diagnostic assistance.
"""
from native_adapter import parse_action as parse_bare_action


def normalize_policy_output(raw):
    text = raw.strip()
    if text.startswith('```'):
        lines = text.splitlines()
        if len(lines) < 3 or lines[0] not in ('```json', '```') or lines[-1] != '```':
            raise ValueError('Output is not exactly one complete JSON code fence')
        if any(line.strip().startswith('```') for line in lines[1:-1]):
            raise ValueError('Multiple or nested code fences are not accepted')
        text = '\n'.join(lines[1:-1]).strip()
    return text


def parse_action(raw):
    return parse_bare_action(normalize_policy_output(raw))
