---
skill_id: request_id_trace
name: Request ID Trace
version: 1
priority: 0.5
error_category: support_investigation
applicable_modes: [all]
applicable_phases: [think]
system_summary: Trace a failing checkout request ID through correlated logs when that trace remains unexplored.
anchor:
  level: step
  trigger: "Checkout failure has endpoint and request ID and its trace is not exhausted"
  evidence: deterministic
  action: inject an investigation instruction
---

# Request ID Trace

Trace a failing checkout request ID through correlated logs when that trace remains unexplored.

This experimental PF reads observed facts from `ctx.raw["support_evidence"]`.
It checks its own prerequisites and injects an instruction. It does not select,
rank, disable, or compare other PFs. All five support cards have equal priority.

