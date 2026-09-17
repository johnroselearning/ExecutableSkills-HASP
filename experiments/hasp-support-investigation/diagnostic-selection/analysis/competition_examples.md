# Representative full stage records

Post-run illustrations selected to show a benefit, a degradation despite all-eligible selection, failure with all-eligible explicit comparison guidance, an omitted-bundle contrast, and preservation without feedback. These examples do not replace aggregate results.

## S06-t02-B

Eligible: evidence_collection, comparison_experiment, dependency_trace. Selected: ['evidence_collection']. Activated: ['evidence_collection'].

All five gates: `{"evidence_collection": true, "request_id_trace": false, "comparison_experiment": true, "dependency_trace": true, "binary_isolation": false}`.

Base proposal:
```
```json
{
  "action": "C",
  "reason": "The trace shows a 500 error inside the checkout process before payment, and the previous action noted a lack of finer exception detail. Inspecting the backend exception/logs is the most direct next step to find the root cause of the 500 error."
}
```
```

Actual interventions in dispatch order:

[evidence_collection @step] Missing evidence: request_captured. Capture the failing request with method, URL, headers, body, response, timestamp and correlation ID; redact credentials.

Policy revision:
```
```json
{
  "action": "D",
  "reason": "The system explicitly requests capturing the failing request details (headers, body, response). Action D, 'Compare request headers and payload,' captures this information from both clients, which is necessary context to proceed, especially since the initial comparison highlighted a difference (500 vs 200)."
}
```
```

Executed action: **D**. Base score: 0.25; final score: 1; difference: 0.75. Offline best action(s): D. Final action cost: 1.

## S05-t01-B

Eligible: evidence_collection, request_id_trace. Selected: ['evidence_collection', 'request_id_trace']. Activated: ['evidence_collection', 'request_id_trace'].

All five gates: `{"evidence_collection": true, "request_id_trace": true, "comparison_experiment": false, "dependency_trace": false, "binary_isolation": false}`.

Base proposal:
```
```json
{
  "action": "C",
  "reason": "The checkout returns an HTTP 500 error, indicating a backend failure. Since dependency health checks (E) passed and payment wasn't invoked, inspecting the full backend exception and logs (C) is the most direct next step to find the root cause of the 500."
}
```
```

Actual interventions in dispatch order:

[evidence_collection @step] Missing evidence: request_captured. Capture the failing request with method, URL, headers, body, response, timestamp and correlation ID; redact credentials.

[request_id_trace @step] Trace request abc123 for /api/checkout through gateway and application logs. Locate the first failing span and its error details; correlate by request ID and timestamp.

Policy revision:
```
```json
{
  "action": "A",
  "reason": "The system feedback indicates a missing request capture and suggests tracing the request ID. Action A ('Trace request ID') directly addresses the need to inspect the complete request spans and failure boundary using the available correlation ID, which is the best way to locate the failing span mentioned in the feedback."
}
```
```

Executed action: **A**. Base score: 0.333333; final score: 0; difference: -0.333333. Offline best action(s): B, D. Final action cost: 3.

## S08-t01-C

Eligible: evidence_collection, request_id_trace, comparison_experiment. Selected: None. Activated: ['evidence_collection', 'request_id_trace', 'comparison_experiment'].

All five gates: `{"evidence_collection": true, "request_id_trace": true, "comparison_experiment": true, "dependency_trace": false, "binary_isolation": false}`.

Base proposal:
```
```json
{
  "action": "C",
  "reason": "The initial steps showed a mismatch (Web 500 vs Mobile 200) and confirmed that the payment dependency itself is healthy. The next logical step is to inspect the backend logs directly to find the specific exception causing the 500 error on the web client."
}
```
```

Actual interventions in dispatch order:

[evidence_collection @step] Missing evidence: request_captured. Capture the failing request with method, URL, headers, body, response, timestamp and correlation ID; redact credentials.

[request_id_trace @step] Trace request abc123 for /api/checkout through gateway and application logs. Locate the first failing span and its error details; correlate by request ID and timestamp.

[comparison_experiment @step] Compare the failing web request with a successful mobile request for the same account and operation. Hold account, cart, timing and backend constant; compare headers and payloads, then replay one changed factor at a time in a test environment to check whether the failure follows it.

Policy revision:
```
```json
{
  "action": "A",
  "reason": "The system feedback suggests capturing the failing request and tracing the request ID. Action 'A' ('Trace request ID') directly addresses tracing the request through the gateway and application logs to locate the first failing span, which is crucial given the evidence collection feedback."
}
```
```

Executed action: **A**. Base score: 0.25; final score: 0; difference: -0.25. Offline best action(s): D. Final action cost: 3.

## S07-t01-B

Eligible: dependency_trace, binary_isolation. Selected: ['request_id_trace']. Activated: [].

All five gates: `{"evidence_collection": false, "request_id_trace": false, "comparison_experiment": false, "dependency_trace": true, "binary_isolation": true}`.

Base proposal:
```
```json
{
  "action": "C",
  "reason": "The previous checks (A and D) confirmed a 500 error at the checkout API level without providing the underlying exception details. Inspecting the backend exception/logs (C) is the most direct next step to find the root cause of the 500 error."
}
```
```

Actual interventions in dispatch order:

None; no feedback-triggered revision.

Executed action: **C**. Base score: 0; final score: 0; difference: 0. Offline best action(s): B. Final action cost: 4.

## S07-t01-C

Eligible: dependency_trace, binary_isolation. Selected: None. Activated: ['dependency_trace', 'binary_isolation'].

All five gates: `{"evidence_collection": false, "request_id_trace": false, "comparison_experiment": false, "dependency_trace": true, "binary_isolation": true}`.

Base proposal:
```
```json
{
  "action": "C",
  "reason": "The previous checks (A and D) confirmed a 500 error at the checkout API level without providing the underlying exception details. Inspecting the backend exception/logs (C) is the most direct next step to find the root cause of the 500 error."
}
```
```

Actual interventions in dispatch order:

[dependency_trace @step] Inspect checkout calls to cart, inventory and payment services. Check per-request status, latency, routing and input propagation; a successful mobile checkout or unchanged backend version does not exclude a dependency failure caused by different web inputs.

[binary_isolation @step] In a test reproduction, bisect the differing header set or frontend deployment changes against a known-good control. Test both halves and their combination, allowing for interacting changes; retain the smallest set that reproduces the failure and verify by reintroduction.

Policy revision:
```
```json
{
  "action": "F",
  "reason": "Given the system feedback suggesting checking dependency interactions (dependency_trace) and bisecting changes (binary_isolation), the 'Controlled isolation replay suite' (F) is the most comprehensive action. It allows for substituting payloads and stubs to systematically verify the checkout process against known-good or suspected components, directly addressing the need to isolate failing dependencies or differing client inputs."
}
```
```

Executed action: **F**. Base score: 0; final score: 0.2; difference: 0.2. Offline best action(s): B. Final action cost: 5.

## S03-t03-B

Eligible: evidence_collection, request_id_trace, dependency_trace. Selected: ['comparison_experiment']. Activated: [].

All five gates: `{"evidence_collection": true, "request_id_trace": true, "comparison_experiment": false, "dependency_trace": true, "binary_isolation": false}`.

Base proposal:
```
```json
{
  "action": "B",
  "reason": "The previous action (C) revealed an exception during normalization, but it's unclear if this is client-side data formatting or a general backend issue. Comparing web and mobile client submissions (B) will help determine if the input data causing the normalization error differs between clients, narrowing the scope for investigation."
}
```
```

Actual interventions in dispatch order:

None; no feedback-triggered revision.

Executed action: **B**. Base score: 1; final score: 1; difference: 0. Offline best action(s): B. Final action cost: 1.

