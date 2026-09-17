# Complete offline evidence matrix

**Reviewer-only; never send to the policy or selector.**

Compatibility means consistent within these four single-fault worlds, not proof of causality.

| Hypothesis | Definition |
|---|---|
| H1 | Web serializer sends amount as string; current backend raises at checkout normalization. Mobile numeric amount succeeds. |
| H2 | Web omits auth scope header; middleware incorrectly converts scope rejection into 500. Mobile has scope and succeeds. |
| H3 | Shared backend amount-normalization regression rejects both numeric and string amounts. A harmless web string-format difference coexists. |
| H4 | Shared payment failure affects matched web and mobile checkout; request encoding and auth are valid. |

| Action | Cost | Possible observation | Compatible | Eliminates from all four |
|---|---:|---|---|---|
| A — Trace request ID | 3 | abc123: POST /api/checkout returns 500 inside checkout before a payment call. The complete trace has no finer exception detail; no uninspected spans remain. | H1, H2, H3 | H4 |
| A — Trace request ID | 3 | abc123: POST /api/checkout returns 500 after its payment span returns 503. No uninspected spans remain. | H4 | H1, H2, H3 |
| B — Compare web versus mobile | 1 | Matched account, cart, payment method, time and backend: web returns 500; mobile returns 200. | H1, H2 | H3, H4 |
| B — Compare web versus mobile | 1 | Matched account, cart, payment method, time and backend: both web and mobile return 500. | H3, H4 | H1, H2 |
| C — Inspect backend exception/logs | 4 | abc123 exception: CheckoutNormalizationError at normalize_amount, before dependency invocation. The log omits the argument and does not distinguish a bad input from a normalizer regression. | H1, H3 | H2, H4 |
| C — Inspect backend exception/logs | 4 | abc123 exception: required checkout scope missing; middleware converted the authorization exception into HTTP 500. | H2 | H1, H3, H4 |
| C — Inspect backend exception/logs | 4 | abc123 exception: PaymentUnavailable, downstream status 503. | H4 | H1, H2, H3 |
| D — Compare request headers and payload | 1 | Captures for POST /api/checkout (web request-id abc123): credentials and checkout scope match. Web Content-Type application/json;charset=utf-8, X-Checkout-Version web-42, amount "1200" (string); mobile application/json, mobile-17, amount 1200 (number). No replay or client success result has been obtained by this check. | H1, H3 | H2, H4 |
| D — Compare request headers and payload | 1 | Captures for POST /api/checkout (web request-id abc123): equivalent numeric payloads; web lacks X-Checkout-Scope, mobile includes it. Content-Type and X-Checkout-Version also differ. No replay has run. | H2 | H1, H3, H4 |
| D — Compare request headers and payload | 1 | Captures for POST /api/checkout (web request-id abc123): equivalent numeric payloads and checkout scope; only Content-Type charset spelling and X-Checkout-Version differ. No replay has run. | H4 | H1, H2, H3 |
| E — Check payment/dependency health | 2 | Incident-window cart, inventory and payment probes succeed. The failed checkout has no failed downstream calls; payment was not invoked. | H1, H2, H3 | H4 |
| E — Check payment/dependency health | 2 | Incident-window payment probes and this checkout’s payment span return 503; cart and inventory are healthy. | H4 | H1, H2, H3 |
| F — Controlled isolation replay suite | 5 | Replay: only replacing web string amount with numeric amount restores success; reintroducing string restores 500. Auth swaps, backend rollback and payment stub do not fix the string request. | H1 | H2, H3, H4 |
| F — Controlled isolation replay suite | 5 | Replay: adding checkout scope restores success; removing it restores 500. Payload swap, backend rollback and payment stub do not fix missing scope. | H2 | H1, H3, H4 |
| F — Controlled isolation replay suite | 5 | Replay: both payload representations fail on current backend and succeed on previous backend; redeploying current backend restores failure. Auth swaps and payment stub do not fix it. | H3 | H1, H2, H4 |
| F — Controlled isolation replay suite | 5 | Replay: payment stub restores success for both clients; reconnecting failed payment restores 500. Payload/auth swaps and backend rollback do not fix it. | H4 | H1, H2, H3 |
