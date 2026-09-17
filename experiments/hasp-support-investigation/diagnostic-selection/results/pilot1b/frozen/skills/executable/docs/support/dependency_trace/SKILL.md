---
skill_id: dependency_trace
name: Dependency Trace
version: 1
priority: 0.5
error_category: support_investigation
applicable_modes: [all]
applicable_phases: [think]
system_summary: Inspect checkout downstream calls for input-specific failures while dependency behavior is unverified.
anchor:
  level: step
  trigger: "Checkout failure has an endpoint and downstream dependencies remain unverified"
  evidence: deterministic
  action: inject an investigation instruction
---

# Dependency Trace

Inspect checkout downstream calls for input-specific failures while dependency behavior is unverified.

This experimental PF reads observed facts from `ctx.raw["support_evidence"]`.
It checks its own prerequisites and injects an instruction. It does not select,
rank, disable, or compare other PFs. All five support cards have equal priority.

