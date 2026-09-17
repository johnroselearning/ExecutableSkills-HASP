# Pilot 1b — interface-only amendment, before inference

Pilot 1 remains a legitimate, unchanged recorded result: completed attempts, diagnostic
comparison not reached due to policy-output interface failure. It is not bad data and
will not be cleaned, rescored or overwritten.

The ONLY intended methodological difference from Pilot 1 is accepting a complete
policy/revision JSON object wrapped in exactly one whole-output Markdown fence, with
`json` or no language marker, in addition to the previously accepted bare JSON.
Normalization strips outer whitespace, verifies the complete outer fence, removes it,
and passes the result to the original json.loads/schema/action validator. Surrounding
prose, multiple objects, malformed JSON, unknown actions and missing fields still
fail. There is no arbitrary extraction, repair, retry, inference or fallback.

Implementation: new pilot1b_parser.py delegates schema validation to unchanged
native_adapter.parse_action. New pilot1b_runner.py binds this parser and the new output
location into the original unchanged pilot_runner.py. No original source is edited.
Run labeling, freezing and output path change to pilot1b; these are bookkeeping only.
The original loop, messages, selector, native dispatcher, oracle, evaluator, hypotheses,
costs, actions A–F, sampling, role/step seed formula, eight-step cap and stopping rule
remain byte-identical to Pilot 1. No Ollama structured/JSON output mode is enabled.

Exactly 80 attempts: H1/H2/H3/H4 × five trial seeds 101–105 × A, B, C, B_reverse.
A/B/C remain the 60 primary attempts. B_reverse remains a separate 20-attempt order
sensitivity analysis. Initial proposals are generated anew for this run; only the
same five within-run initial proposals are shared across worlds/arms, exactly as
before. Historical Pilot 1 proposals are used only in an offline parser contract test,
never as inputs, executed actions or diagnostic scores in either run.

Before any inference, all five historical raw responses must validate, with raw and
normalized text/actions saved in a new audit. Positive/negative contract tests must
pass. Hash and freeze parser, original/new runners, evaluator, oracle, hypotheses,
actions, native adapter, native HASP files, support PF documents and this protocol.
Also preserve a pre-run digest inventory of all pre-existing experiment artifacts.
No evaluator changes are authorized in response to results.

Runtime unchanged: installed gemma4e-64k:latest (parent gemma4:e4b, Q4_K_M), local
Ollama 0.31.2 via localhost:11435, Vulkan Radeon 780M, 8 host threads, temperature 0.7,
top_p 1, top_k 64, repeat_penalty 1.0, context 4096, think=false; token caps 256 policy,
256 selector, 512 revision. Model blob digest remains
sha256:4c27e0f5b5adf02ac956c7322bd2ee7636fe3f45a8512c9aba5385242cb6e09a.
No paid API, no downloads, no model change, no new feasibility inference required.
Same expected call range 285–465 for 2–3 steps, conservative ceiling 1,365; no assurance
of trajectory length. Prior smoke/policy calls took seconds each; roughly 20–90 minutes
is a loose planning range with cache/prefill uncertainty, not a new stopping rule.

Record raw selector output, selected IDs, actual gates, firings/interventions, base
proposal, revision, executed action, observed evidence, and offline per-action scores
in original step records. Best actions are derived offline as rank==1. Score only
executed actions, not PF names. For B/C (and separately B_reverse), compare the base
proposal's offline score with the executed action's score in the SAME observed state:
improved, unchanged or worse. Report this as descriptive association, not causal proof.
A changed action with equal score remains an unchanged-score change. Invalid outputs
remain failures and are never treated as low-cost successes. F remains a legitimate
isolation action with its own cost/step tradeoff.

Produce PILOT1B_RESULTS.md, full representative trajectories and machine-readable
summaries. Report per-world/arm validity, first executed actions, expected-optimal and
top-2 rates, isolation, costs, steps, zero-information checks/repeats, PF frequencies,
proposal→execution changes and helpful/harmful score changes. Keep pooled step rates
separate from mean per-episode rates; state shared first-proposal dependence and n=5
limitations. Native selection primitives are still a support-step adaptation, not a
claim of an untouched stock terminal-answer benchmark. Preserve all earlier limitations.

Stop after this pilot. No larger experiment and no proposed strategy selector.
