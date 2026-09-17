---
skill_id: binary_isolation
name: Binary Isolation
version: 1
priority: 0.5
error_category: support_investigation
applicable_modes: [all]
applicable_phases: [think]
system_summary: Bisect differing request headers or frontend changes between failing and successful checkout reproductions.
anchor:
  level: step
  trigger: "Checkout failure has multiple differing headers or a frontend deployment change set"
  evidence: deterministic
  action: inject an investigation instruction
---

# Binary Isolation

Bisect differing request headers or frontend changes between failing and successful checkout reproductions.

This experimental PF reads observed facts from `ctx.raw["support_evidence"]`.
It checks its own prerequisites and injects an instruction. It does not select,
rank, disable, or compare other PFs. All five support cards have equal priority.

