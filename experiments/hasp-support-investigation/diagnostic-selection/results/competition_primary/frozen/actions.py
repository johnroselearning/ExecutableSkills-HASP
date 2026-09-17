"""Public action interface; no outcome or scoring information."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Action:
    name: str
    cost: int
    scope: str

ACTIONS = {
    'A': Action('Trace request ID', 3, 'Collect correlation ID if absent; inspect complete request spans and failure boundary.'),
    'B': Action('Compare web versus mobile', 1, 'Matched account, cart, payment, time and backend; reproduce on both clients.'),
    'C': Action('Inspect backend exception/logs', 4, 'Read the full exception and correlated application log for this checkout.'),
    'D': Action('Compare request headers and payload', 1, 'Capture both clients; compare credentials, content types and bodies; no causal replay.'),
    'E': Action('Check payment/dependency health', 2, 'Check incident-window dependency probes AND this request’s downstream outcomes.'),
    'F': Action('Controlled isolation replay suite', 5, 'Sandbox payload/auth substitutions, current/previous backend and dependency stub; verify by reintroduction.'),
}

def public_actions():
    return {key: vars(value) for key, value in ACTIONS.items()}
