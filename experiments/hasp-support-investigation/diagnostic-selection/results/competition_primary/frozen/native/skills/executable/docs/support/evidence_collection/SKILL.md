---
skill_id: evidence_collection
name: Evidence Collection
version: 1
priority: 0.5
error_category: support_investigation
applicable_modes: [all]
applicable_phases: [think]
system_summary: Collect missing endpoint, request ID, and request capture for a checkout failure.
anchor:
  level: step
  trigger: "Checkout failure lacks an endpoint, request ID, or captured request"
  evidence: deterministic
  action: inject an investigation instruction
---

# Evidence Collection

Collect missing endpoint, request ID, and request capture for a checkout failure.

This experimental PF reads observed facts from `ctx.raw["support_evidence"]`.
It checks its own prerequisites and injects an instruction. It does not select,
rank, disable, or compare other PFs. All five support cards have equal priority.

