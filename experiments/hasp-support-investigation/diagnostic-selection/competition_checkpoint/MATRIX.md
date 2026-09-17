# Fixed competition snapshot matrix

Offline score = expected eliminations / action cost under the unchanged uniform viable-world evaluator. T/F are actual native wrapper gate results with all fire counts zero.

PF1 evidence_collection; PF2 request_id_trace; PF3 comparison_experiment; PF4 dependency_trace; PF5 binary_isolation.

| Snapshot | Oracle history / public evidence | Viable worlds (offline) | PF1 | PF2 | PF3 | PF4 | PF5 | Eligible | Scores A / B / C / D / E / F | Best |
|---|---|---|---|---|---|---|---|---:|---|---|
| S01 | A | H1, H2, H3 | T | F | F | T | F | 2 | 0 / 1.33333 / 0.333333 / 1.33333 / 0 / 0.4 | B, D |
| S02 | B | H1, H2 | T | F | T | F | F | 2 | 0 / 0 / 0.25 / 1 / 0 / 0.2 | D |
| S03 | C | H1, H3 | T | T | F | T | F | 3 | 0 / 1 / 0 / 0 / 0 / 0.2 | B |
| S04 | D | H1, H3 | F | T | F | T | T | 3 | 0 / 1 / 0 / 0 / 0 / 0.2 | B |
| S05 | E | H1, H2, H3 | T | T | F | F | F | 2 | 0 / 1.33333 / 0.333333 / 1.33333 / 0 / 0.4 | B, D |
| S06 | AB | H1, H2 | T | F | T | T | F | 3 | 0 / 0 / 0.25 / 1 / 0 / 0.2 | D |
| S07 | AD | H1, H3 | F | F | F | T | T | 2 | 0 / 1 / 0 / 0 / 0 / 0.2 | B |
| S08 | BE | H1, H2 | T | T | T | F | F | 3 | 0 / 0 / 0.25 / 1 / 0 / 0.2 | D |
| S09 | CE | H1, H3 | T | T | F | F | F | 2 | 0 / 1 / 0 / 0 / 0 / 0.2 | B |
| S10 | DE | H1, H3 | F | T | F | F | T | 2 | 0 / 1 / 0 / 0 / 0 / 0.2 | B |

## Exact evidence visible to the model

The public action menu and exact complete messages are in `prompt_flows.json`. Only problem, observed history (action, observation, cost) and public actions enter policy messages. Structured facts below are native gate inputs, not an additional model message. No world label, score, rank, gate matrix or best action enters model messages.

### S01

```json
{
  "problem": "Checkout returns HTTP 500. No root cause is known.",
  "observed_history": [
    {
      "action": "A",
      "observation": "abc123: POST /api/checkout returns 500 inside checkout before a payment call. The complete trace has no finer exception detail; no uninspected spans remain.",
      "cost": 3
    }
  ]
}
```

Native gate evidence:
```json
{
  "operation": "checkout",
  "status": 500,
  "endpoint": "/api/checkout",
  "method": "POST",
  "request_id": "abc123",
  "trace_exhausted": true
}
```

### S02

```json
{
  "problem": "Checkout returns HTTP 500. No root cause is known.",
  "observed_history": [
    {
      "action": "B",
      "observation": "Matched account, cart, payment method, time and backend: web returns 500; mobile returns 200.",
      "cost": 1
    }
  ]
}
```

Native gate evidence:
```json
{
  "operation": "checkout",
  "status": 500,
  "web_fails": true,
  "mobile_succeeds": true,
  "same_account": true,
  "same_operation": true
}
```

### S03

```json
{
  "problem": "Checkout returns HTTP 500. No root cause is known.",
  "observed_history": [
    {
      "action": "C",
      "observation": "abc123 exception: CheckoutNormalizationError at normalize_amount, before dependency invocation. The log omits the argument and does not distinguish a bad input from a normalizer regression.",
      "cost": 4
    }
  ]
}
```

Native gate evidence:
```json
{
  "operation": "checkout",
  "status": 500,
  "endpoint": "/api/checkout",
  "method": "POST",
  "request_id": "abc123"
}
```

### S04

```json
{
  "problem": "Checkout returns HTTP 500. No root cause is known.",
  "observed_history": [
    {
      "action": "D",
      "observation": "Captures for POST /api/checkout (web request-id abc123): credentials and checkout scope match. Web Content-Type application/json;charset=utf-8, X-Checkout-Version web-42, amount \"1200\" (string); mobile application/json, mobile-17, amount 1200 (number). No replay or client success result has been obtained by this check.",
      "cost": 1
    }
  ]
}
```

Native gate evidence:
```json
{
  "operation": "checkout",
  "status": 500,
  "endpoint": "/api/checkout",
  "method": "POST",
  "request_id": "abc123",
  "request_captured": true,
  "differing_headers": [
    "Content-Type",
    "X-Checkout-Version"
  ]
}
```

### S05

```json
{
  "problem": "Checkout returns HTTP 500. No root cause is known.",
  "observed_history": [
    {
      "action": "E",
      "observation": "Incident-window cart, inventory and payment probes succeed. The failed checkout has no failed downstream calls; payment was not invoked.",
      "cost": 2
    }
  ]
}
```

Native gate evidence:
```json
{
  "operation": "checkout",
  "status": 500,
  "endpoint": "/api/checkout",
  "method": "POST",
  "request_id": "abc123",
  "dependencies_verified_successful": true
}
```

### S06

```json
{
  "problem": "Checkout returns HTTP 500. No root cause is known.",
  "observed_history": [
    {
      "action": "A",
      "observation": "abc123: POST /api/checkout returns 500 inside checkout before a payment call. The complete trace has no finer exception detail; no uninspected spans remain.",
      "cost": 3
    },
    {
      "action": "B",
      "observation": "Matched account, cart, payment method, time and backend: web returns 500; mobile returns 200.",
      "cost": 1
    }
  ]
}
```

Native gate evidence:
```json
{
  "operation": "checkout",
  "status": 500,
  "endpoint": "/api/checkout",
  "method": "POST",
  "request_id": "abc123",
  "trace_exhausted": true,
  "web_fails": true,
  "mobile_succeeds": true,
  "same_account": true,
  "same_operation": true
}
```

### S07

```json
{
  "problem": "Checkout returns HTTP 500. No root cause is known.",
  "observed_history": [
    {
      "action": "A",
      "observation": "abc123: POST /api/checkout returns 500 inside checkout before a payment call. The complete trace has no finer exception detail; no uninspected spans remain.",
      "cost": 3
    },
    {
      "action": "D",
      "observation": "Captures for POST /api/checkout (web request-id abc123): credentials and checkout scope match. Web Content-Type application/json;charset=utf-8, X-Checkout-Version web-42, amount \"1200\" (string); mobile application/json, mobile-17, amount 1200 (number). No replay or client success result has been obtained by this check.",
      "cost": 1
    }
  ]
}
```

Native gate evidence:
```json
{
  "operation": "checkout",
  "status": 500,
  "endpoint": "/api/checkout",
  "method": "POST",
  "request_id": "abc123",
  "trace_exhausted": true,
  "request_captured": true,
  "differing_headers": [
    "Content-Type",
    "X-Checkout-Version"
  ]
}
```

### S08

```json
{
  "problem": "Checkout returns HTTP 500. No root cause is known.",
  "observed_history": [
    {
      "action": "B",
      "observation": "Matched account, cart, payment method, time and backend: web returns 500; mobile returns 200.",
      "cost": 1
    },
    {
      "action": "E",
      "observation": "Incident-window cart, inventory and payment probes succeed. The failed checkout has no failed downstream calls; payment was not invoked.",
      "cost": 2
    }
  ]
}
```

Native gate evidence:
```json
{
  "operation": "checkout",
  "status": 500,
  "web_fails": true,
  "mobile_succeeds": true,
  "same_account": true,
  "same_operation": true,
  "endpoint": "/api/checkout",
  "method": "POST",
  "request_id": "abc123",
  "dependencies_verified_successful": true
}
```

### S09

```json
{
  "problem": "Checkout returns HTTP 500. No root cause is known.",
  "observed_history": [
    {
      "action": "C",
      "observation": "abc123 exception: CheckoutNormalizationError at normalize_amount, before dependency invocation. The log omits the argument and does not distinguish a bad input from a normalizer regression.",
      "cost": 4
    },
    {
      "action": "E",
      "observation": "Incident-window cart, inventory and payment probes succeed. The failed checkout has no failed downstream calls; payment was not invoked.",
      "cost": 2
    }
  ]
}
```

Native gate evidence:
```json
{
  "operation": "checkout",
  "status": 500,
  "endpoint": "/api/checkout",
  "method": "POST",
  "request_id": "abc123",
  "dependencies_verified_successful": true
}
```

### S10

```json
{
  "problem": "Checkout returns HTTP 500. No root cause is known.",
  "observed_history": [
    {
      "action": "D",
      "observation": "Captures for POST /api/checkout (web request-id abc123): credentials and checkout scope match. Web Content-Type application/json;charset=utf-8, X-Checkout-Version web-42, amount \"1200\" (string); mobile application/json, mobile-17, amount 1200 (number). No replay or client success result has been obtained by this check.",
      "cost": 1
    },
    {
      "action": "E",
      "observation": "Incident-window cart, inventory and payment probes succeed. The failed checkout has no failed downstream calls; payment was not invoked.",
      "cost": 2
    }
  ]
}
```

Native gate evidence:
```json
{
  "operation": "checkout",
  "status": 500,
  "endpoint": "/api/checkout",
  "method": "POST",
  "request_id": "abc123",
  "request_captured": true,
  "differing_headers": [
    "Content-Type",
    "X-Checkout-Version"
  ],
  "dependencies_verified_successful": true
}
```
