# PF action coverage — frozen before inference

Does at least one eligible PF intervention explicitly provide guidance that could naturally lead to one of the offline-best diagnostic actions?

Interpretation-only bundle coverage; not a best-PF oracle, selection target, or success score.

These are subjective bundle annotations, not PF utility/rank/correctness labels. Clear support does not mean the entire bundle recommends the optimum. Ambiguous support is deliberately a weak reading of known-good-control guidance. Categories are not randomized groups and never enter prompts or optimal-action scoring.

## S01

Eligible: evidence_collection, dependency_trace. All fire counts initially zero.

Offline best: B, D. **CLEAR_SUPPORT**.

The missing-evidence intervention explicitly asks to capture request headers and body, which naturally supports D. No claim is made that it specifically endorses both tied best actions B and D.

### evidence_collection

[evidence_collection @step] Missing evidence: request_captured. Capture the failing request with method, URL, headers, body, response, timestamp and correlation ID; redact credentials.

### dependency_trace

[dependency_trace @step] Inspect checkout calls to cart, inventory and payment services. Check per-request status, latency, routing and input propagation; a successful mobile checkout or unchanged backend version does not exclude a dependency failure caused by different web inputs.

## S02

Eligible: evidence_collection, comparison_experiment. All fire counts initially zero.

Offline best: D. **CLEAR_SUPPORT**.

The bundle explicitly asks to compare failing web and successful mobile request headers and payloads, naturally supporting D.

### evidence_collection

[evidence_collection @step] Missing evidence: endpoint, request_id, request_captured. Capture the failing request with method, URL, headers, body, response, timestamp and correlation ID; redact credentials.

### comparison_experiment

[comparison_experiment @step] Compare the failing web request with a successful mobile request for the same account and operation. Hold account, cart, timing and backend constant; compare headers and payloads, then replay one changed factor at a time in a test environment to check whether the failure follows it.

## S03

Eligible: evidence_collection, request_id_trace, dependency_trace. All fire counts initially zero.

Offline best: B. **NO_CLEAR_SUPPORT**.

The bundle asks for request capture, correlated tracing and dependency inspection. None explicitly asks to reproduce on both matched clients, the best action B; capture alone is not that experiment.

### evidence_collection

[evidence_collection @step] Missing evidence: request_captured. Capture the failing request with method, URL, headers, body, response, timestamp and correlation ID; redact credentials.

### request_id_trace

[request_id_trace @step] Trace request abc123 for /api/checkout through gateway and application logs. Locate the first failing span and its error details; correlate by request ID and timestamp.

### dependency_trace

[dependency_trace @step] Inspect checkout calls to cart, inventory and payment services. Check per-request status, latency, routing and input propagation; a successful mobile checkout or unchanged backend version does not exclude a dependency failure caused by different web inputs.

## S04

Eligible: request_id_trace, dependency_trace, binary_isolation. All fire counts initially zero.

Offline best: B. **AMBIGUOUS_SUPPORT**.

Isolation asks for a test reproduction against a known-good control. Establishing a matched mobile control could lead to B, but the intervention does not name that client comparison and instead prescribes bisection. Dependency text mentions mobile success only as a caveat, not an instruction to run B.

### request_id_trace

[request_id_trace @step] Trace request abc123 for /api/checkout through gateway and application logs. Locate the first failing span and its error details; correlate by request ID and timestamp.

### dependency_trace

[dependency_trace @step] Inspect checkout calls to cart, inventory and payment services. Check per-request status, latency, routing and input propagation; a successful mobile checkout or unchanged backend version does not exclude a dependency failure caused by different web inputs.

### binary_isolation

[binary_isolation @step] In a test reproduction, bisect the differing header set or frontend deployment changes against a known-good control. Test both halves and their combination, allowing for interacting changes; retain the smallest set that reproduces the failure and verify by reintroduction.

## S05

Eligible: evidence_collection, request_id_trace. All fire counts initially zero.

Offline best: B, D. **CLEAR_SUPPORT**.

The missing-evidence intervention explicitly asks for request headers and body capture, naturally supporting tied-best D. The trace guidance does not itself establish best-action support.

### evidence_collection

[evidence_collection @step] Missing evidence: request_captured. Capture the failing request with method, URL, headers, body, response, timestamp and correlation ID; redact credentials.

### request_id_trace

[request_id_trace @step] Trace request abc123 for /api/checkout through gateway and application logs. Locate the first failing span and its error details; correlate by request ID and timestamp.

## S06

Eligible: evidence_collection, comparison_experiment, dependency_trace. All fire counts initially zero.

Offline best: D. **CLEAR_SUPPORT**.

The comparison intervention explicitly asks to compare matched failing web and successful mobile headers and payloads, naturally supporting D.

### evidence_collection

[evidence_collection @step] Missing evidence: request_captured. Capture the failing request with method, URL, headers, body, response, timestamp and correlation ID; redact credentials.

### comparison_experiment

[comparison_experiment @step] Compare the failing web request with a successful mobile request for the same account and operation. Hold account, cart, timing and backend constant; compare headers and payloads, then replay one changed factor at a time in a test environment to check whether the failure follows it.

### dependency_trace

[dependency_trace @step] Inspect checkout calls to cart, inventory and payment services. Check per-request status, latency, routing and input propagation; a successful mobile checkout or unchanged backend version does not exclude a dependency failure caused by different web inputs.

## S07

Eligible: dependency_trace, binary_isolation. All fire counts initially zero.

Offline best: B. **AMBIGUOUS_SUPPORT**.

Isolation calls for a test reproduction against a known-good control, which could motivate establishing the matched mobile baseline B. It does not explicitly request web/mobile reproduction; bisection and downstream inspection are its direct guidance.

### dependency_trace

[dependency_trace @step] Inspect checkout calls to cart, inventory and payment services. Check per-request status, latency, routing and input propagation; a successful mobile checkout or unchanged backend version does not exclude a dependency failure caused by different web inputs.

### binary_isolation

[binary_isolation @step] In a test reproduction, bisect the differing header set or frontend deployment changes against a known-good control. Test both halves and their combination, allowing for interacting changes; retain the smallest set that reproduces the failure and verify by reintroduction.

## S08

Eligible: evidence_collection, request_id_trace, comparison_experiment. All fire counts initially zero.

Offline best: D. **CLEAR_SUPPORT**.

The comparison intervention explicitly asks to compare matched failing web and successful mobile request headers and payloads, naturally supporting D.

### evidence_collection

[evidence_collection @step] Missing evidence: request_captured. Capture the failing request with method, URL, headers, body, response, timestamp and correlation ID; redact credentials.

### request_id_trace

[request_id_trace @step] Trace request abc123 for /api/checkout through gateway and application logs. Locate the first failing span and its error details; correlate by request ID and timestamp.

### comparison_experiment

[comparison_experiment @step] Compare the failing web request with a successful mobile request for the same account and operation. Hold account, cart, timing and backend constant; compare headers and payloads, then replay one changed factor at a time in a test environment to check whether the failure follows it.

## S09

Eligible: evidence_collection, request_id_trace. All fire counts initially zero.

Offline best: B. **NO_CLEAR_SUPPORT**.

Request capture and correlated tracing do not explicitly direct matched web/mobile reproduction B. The bundle contains no comparison or control-baseline guidance.

### evidence_collection

[evidence_collection @step] Missing evidence: request_captured. Capture the failing request with method, URL, headers, body, response, timestamp and correlation ID; redact credentials.

### request_id_trace

[request_id_trace @step] Trace request abc123 for /api/checkout through gateway and application logs. Locate the first failing span and its error details; correlate by request ID and timestamp.

## S10

Eligible: request_id_trace, binary_isolation. All fire counts initially zero.

Offline best: B. **AMBIGUOUS_SUPPORT**.

The isolation intervention requests a known-good control for test reproduction. This could lead to establishing the matched mobile baseline B, but mobile and the matched-client test are not specified; tracing and bisection are the explicit directions.

### request_id_trace

[request_id_trace @step] Trace request abc123 for /api/checkout through gateway and application logs. Locate the first failing span and its error details; correlate by request ID and timestamp.

### binary_isolation

[binary_isolation @step] In a test reproduction, bisect the differing header set or frontend deployment changes against a known-good control. Test both halves and their combination, allowing for interacting changes; retain the smallest set that reproduces the failure and verify by reintroduction.

