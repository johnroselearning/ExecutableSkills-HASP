---
skill_id: comparison_experiment
name: Comparison Experiment
version: 1
priority: 0.5
error_category: support_investigation
applicable_modes: [all]
applicable_phases: [think]
system_summary: Compare failing web and successful mobile checkout requests for the same account and operation.
anchor:
  level: step
  trigger: "Web checkout fails while mobile succeeds for the same account and operation"
  evidence: deterministic
  action: inject an investigation instruction
---

# Comparison Experiment

Compare failing web and successful mobile checkout requests for the same account and operation.

This experimental PF reads observed facts from `ctx.raw["support_evidence"]`.
It checks its own prerequisites and injects an instruction. It does not select,
rank, disable, or compare other PFs. All five support cards have equal priority.

