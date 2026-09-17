# Pilot 1 — pre-run amendment and runtime feasibility

Approved by user after the design checkpoint. This amendment is written before any
pilot diagnostic inference. The original DESIGN, evaluator, oracle and prompts stay
unchanged. No proposed selector is implemented.

## Scope

Four worlds H1/H2/H3/H4; five seeds each (101–105); A/base, B/native canonical,
C/all retained = 60 primary episodes. B_reverse is a separate 20-episode sensitivity
arm, not pooled into the primary comparison. Start every episode at the initial
complaint; do not cross the five snapshot histories with these worlds. Maximum eight
actions. F remains available: singleton isolation via F is success, with cost and
steps reported separately. Episode identity never enters model messages.

First policy proposals depend only on trial seed because initial public inputs are
identical across all worlds/arms. Cache and share the five initial proposals across
worlds and arms, as in the approved design's proposal-reuse plan. Report these as five
unique samples, not 80 independent first-proposal samples. Subsequent proposal calls
use observed history. Selector/revision seeds are separated by role and step. Same
seed does not guarantee bitwise reproducibility. Rotate world and arm schedule by
trial; no cross-episode messages or feedback. Ollama may reuse computational prefix
caches, which are not conversation memory.

## Feasible runtime

- Model tag: `gemma4e-64k:latest`, installed parent `gemma4:e4b`.
- Local model metadata: gemma4 family, 8.0B parameter size, GGUF Q4_K_M.
- Model blob digest: sha256:4c27e0f5b5adf02ac956c7322bd2ee7636fe3f45a8512c9aba5385242cb6e09a.
- Runtime: Ollama 0.31.2, isolated localhost:11435; cloud disabled, no downloads.
- Hardware: AMD Radeon 780M iGPU via Vulkan, native log confirms 43/43 layers
  offloaded; Ryzen 7 PRO 8840HS host with 8 inference threads. GPU discovery succeeded
  outside the restricted process even though the initial sandbox inspection found none.
- Temperature 0.7; top_p 1; top_k 64 (model default, made explicit); repeat_penalty 1.0;
  `think=false`; context 4096. No JSON-mode constraint or selector-output repair.
- Output caps: policy 256, selector 256, revision 512 tokens.
- Seed passed through Ollama `options.seed`. Two non-diagnostic identical-seed smoke
  calls returned the same six-token JSON. This verifies parameter acceptance, not
  comprehensive deterministic sampling. Exact requests/responses are saved.
- Approximately 23 output tokens/s on the tiny warm smoke response; first load ~8s.
  The smoke prompt is too small to predict full prompt-prefill and cache behavior.
- Expected calls at 2–3 steps: roughly 285–465 after shared first proposals, fewer
  if native fire caps suppress revisions. Conservative cap: 1,365 diagnostic calls
  (1,440 before 75 shared-proposal savings), plus two completed feasibility calls.
- At output caps: 491,520 tokens before reuse; input planning range
  0.68–4.10M at 500–3,000 assumed tokens/call. These are assumptions, not measurements.
- No paid API charges. Local CPU/iGPU time and electricity only. Planning expectation roughly
  1–3 hours for the pilot, highly uncertain; pathological eight-step episodes could
  take substantially longer. This is not a measured diagnostic throughput forecast.
  Actual call durations/token counts will replace this estimate in results.

## Freeze, failures and reporting

Before diagnostic inference, copy evaluator, hypotheses, actions, oracle, native
adapter, protocol and runner into results/pilot1/frozen; hash them in manifest.json.
Do not edit the evaluator based on model outcomes. If a real bug is found, preserve
this run, document it, and use a new run ID before any rerun. Raw model calls are
append-only in calls.jsonl; step/episode traces are append-only in separate files.

No retries or best-action fallback for invalid policy JSON. Abort the episode and
report it. Empty native PF selection is allowed; unparsed nonempty outputs are
recorded without substituting PFs. Provider failures are terminal and preserved.
Action scores are computed only after final policy generation and are never put
into model messages. Singleton stopping uses the offline evaluator; this evaluates
closed-world evidence isolation, not a model's final causal diagnosis.

Preserve PF selection, actual gates, firing records, full interventions, proposal,
revision and executed tool as distinct fields. Score only executed actions. All-retained
C has null model selection and an explicit retained list. First-action rates are for
executed actions, with shared proposal dependence disclosed. Report per-world and
arm results, B order sensitivity, episode-weighted and pooled decision optimality,
isolation/cost/steps, zero-information and repeated checks, invalid outputs and full
representative trajectories. Treat 5/world/arm as descriptive, not reliable evidence
of population rates or ordering equivalence.

Stop after Pilot 1 and produce PILOT_RESULTS.md. No full experiment or new mechanism.
