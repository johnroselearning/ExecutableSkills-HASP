"""Deterministic host-side oracle. Expose execute() responses, never source, to models."""
from copy import deepcopy
from actions import ACTIONS
from hypotheses import OUTCOMES

INITIAL = 'Checkout returns HTTP 500. No root cause is known.'
BASE_FACTS = {'operation': 'checkout', 'status': 500}
IDENTITY = {'endpoint': '/api/checkout', 'method': 'POST', 'request_id': 'abc123'}
CAPTURE = {**IDENTITY, 'request_captured': True,
           'differing_headers': ['Content-Type', 'X-Checkout-Version']}
OBSERVATIONS = {
 'A': {
  'internal': ('abc123: POST /api/checkout returns 500 inside checkout before a payment call. The complete trace has no finer exception detail; no uninspected spans remain.', {**IDENTITY, 'trace_exhausted': True}),
  'downstream': ('abc123: POST /api/checkout returns 500 after its payment span returns 503. No uninspected spans remain.', {**IDENTITY, 'trace_exhausted': True}),
 },
 'B': {
  'web_only': ('Matched account, cart, payment method, time and backend: web returns 500; mobile returns 200.', {'web_fails': True, 'mobile_succeeds': True, 'same_account': True, 'same_operation': True}),
  'both': ('Matched account, cart, payment method, time and backend: both web and mobile return 500.', {'web_fails': True, 'mobile_succeeds': False, 'same_account': True, 'same_operation': True}),
 },
 'C': {
  'normalize': ('abc123 exception: CheckoutNormalizationError at normalize_amount, before dependency invocation. The log omits the argument and does not distinguish a bad input from a normalizer regression.', IDENTITY),
  'scope': ('abc123 exception: required checkout scope missing; middleware converted the authorization exception into HTTP 500.', IDENTITY),
  'payment': ('abc123 exception: PaymentUnavailable, downstream status 503.', IDENTITY),
 },
 'D': {
  'amount': ('Captures for POST /api/checkout (web request-id abc123): credentials and checkout scope match. Web Content-Type application/json;charset=utf-8, X-Checkout-Version web-42, amount "1200" (string); mobile application/json, mobile-17, amount 1200 (number). No replay or client success result has been obtained by this check.', CAPTURE),
  'scope': ('Captures for POST /api/checkout (web request-id abc123): equivalent numeric payloads; web lacks X-Checkout-Scope, mobile includes it. Content-Type and X-Checkout-Version also differ. No replay has run.', {**CAPTURE, 'differing_headers': ['Content-Type', 'X-Checkout-Version', 'X-Checkout-Scope']}),
  'valid': ('Captures for POST /api/checkout (web request-id abc123): equivalent numeric payloads and checkout scope; only Content-Type charset spelling and X-Checkout-Version differ. No replay has run.', CAPTURE),
 },
 'E': {
  'healthy': ('Incident-window cart, inventory and payment probes succeed. The failed checkout has no failed downstream calls; payment was not invoked.', {**IDENTITY, 'dependencies_verified_successful': True}),
  'failed': ('Incident-window payment probes and this checkout’s payment span return 503; cart and inventory are healthy.', IDENTITY),
 },
 'F': {
  'H1': ('Replay: only replacing web string amount with numeric amount restores success; reintroducing string restores 500. Auth swaps, backend rollback and payment stub do not fix the string request.', CAPTURE),
  'H2': ('Replay: adding checkout scope restores success; removing it restores 500. Payload swap, backend rollback and payment stub do not fix missing scope.', CAPTURE),
  'H3': ('Replay: both payload representations fail on current backend and succeed on previous backend; redeploying current backend restores failure. Auth swaps and payment stub do not fix it.', CAPTURE),
  'H4': ('Replay: payment stub restores success for both clients; reconnecting failed payment restores 500. Payload/auth swaps and backend rollback do not fix it.', CAPTURE),
 },
}

class Oracle:
    def __init__(self, truth='H1'):
        if truth not in OUTCOMES['F']:
            raise ValueError('Unknown host-side world')
        self._truth = truth
        self._history = []

    def execute(self, action):
        if action not in ACTIONS:
            raise ValueError('Unknown diagnostic action')
        observation, facts = OBSERVATIONS[action][OUTCOMES[action][self._truth]]
        record = {'action': action, 'observation': observation,
                  'facts': deepcopy(facts), 'cost': ACTIONS[action].cost}
        self._history.append(record)
        return deepcopy(record)

    def public_state(self):
        facts = deepcopy(BASE_FACTS)
        for record in self._history:
            facts.update(record['facts'])
        return {'problem': INITIAL, 'history': deepcopy(self._history), 'support_evidence': facts}

# Histories, not special policy rules. Every supplied observation is obtained by execute().
CASES = {'initial': [], 'matched_clients': ['B'], 'request_boundary': ['A'],
         'captured_requests': ['D'], 'matched_and_healthy': ['B', 'E']}

def case_oracle(name, truth='H1'):
    oracle = Oracle(truth)
    for action in CASES[name]:
        oracle.execute(action)
    return oracle
