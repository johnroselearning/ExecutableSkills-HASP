# Competition stress test — review checkpoint, no inference authorized

Status: STOPPED BEFORE INFERENCE. Ten fixed, unresolved, oracle-generated snapshots;
ten trials per snapshot per condition; 400 primary condition observations. No trajectory
runs. No additional strategy selector. The offline builder has no model client.

Read MATRIX.md for all five gates, evidence and action scores; snapshots.json for full
precision scores, outcome partitions and actual deterministic C dispatch records;
prompt_flows.json for exact complete message arrays (base proposal placeholders only).
The deterministic dispatch audit calls native PF code without a teacher/model. It is
not an inference result. Fresh zero counts are used independently for every audit/arm.

## Evidence validity and coverage

Every observation and structured fact comes directly from existing Oracle.execute;
no fabricated facts or weakened gates. Every viable world reproduces each snapshot
exactly, including facts. Distinctness is by public evidence, not hidden truth or
history reordering. Prior diagnostics are fixed setup evidence, not model trajectories;
prior costs are not charged to the next chosen action. All snapshots remain unresolved.

Requested competition types:
- A: evidence_collection / dependency_trace: S01 (also in S03, S06).
- B: evidence_collection / request_id_trace / dependency_trace: S03.
- C: comparison_experiment / binary_isolation: unavailable with unresolved uncertainty.
- D: request_id_trace / comparison_experiment: S08, with evidence_collection.
- E: dependency_trace / comparison_experiment: S06, with evidence_collection.
- F: tracing / comparison / isolation: unavailable with unresolved uncertainty.
  S04 has request tracing / dependency tracing / isolation, but no comparison gate.

The exhaustive offline subset audit covers all six diagnostic actions and four worlds.
Comparison requires B's web-only success/failure result (H1/H2); isolation requires
D or F in this oracle. D distinguishes H1/H2, and F resolves any world. Thus every
comparison+isolation overlap is already resolved. Repeated checks or history permutations
do not introduce new outcomes or alter these consistent facts. Do not pad the primary
sample with resolved states, identical evidence under another truth, or order variants.

Ten evidence states contain only three posterior sets and related diagnostic rankings.
There are six two-eligible and four three-eligible snapshots. Gate eligibility does not
imply nonzero marginal information: a still-open trace gate may recommend redundant
checks after other evidence. That is a property under test, not a reason to modify gates.
Do not infer a causal effect of eligible-count from between-snapshot differences.

## Exact A/B/C/D flow

For each snapshot/trial generate ONE base response from native_adapter.policy_messages.
Cache its exact text and call ID, reuse for all four arms. The policy sees only the
initial problem, ordered observations and public A–F action names, costs and scopes.
The selector sees that same public interaction, the exact base response, and the native
PF selector instruction/menu. Offline state never enters either prompt builder.

A: parse and execute the shared base action once; no extra generation.
B: native selector_messages -> native selected_ids parser -> dispatch only parsed IDs
in returned tag order -> native gates -> actual interventions -> native revision_messages
only if interventions exist -> parse/execute final action. With no intervention, execute
the native dispatch argument (normally the base). Do not force an extra B revision.
C: use all and only independently gate-eligible IDs, in this fixed order filtered to
eligibility: evidence_collection, request_id_trace, comparison_experiment,
dependency_trace, binary_isolation. Fresh zero counts; native dispatch and native
revision_messages using actual feedback. No selector call. This is an all-eligible
experimental condition, not native model selection.
D: always one additional generation, same public base conversation and exact base
assistant response, followed by this exact neutral user message:

> Review your proposed diagnostic action once more using only the evidence already available and return your final action. Use the same single-action JSON format.

D contains no PF feedback, PF menu, diagnostic hints, scores or hidden facts. It is a
revision-only control, not native HASP. It matches the extra-turn structure, revision
sampling and token budget, not the feedback content or prompt length. B without feedback
has fewer generations than D; report this subset separately. Do not interpret every
B-minus-D difference as an isolated causal effect of PF selection.

All arms execute only one final action in a fresh clone of the snapshot. Score that
executed action using the PRE-action evidence. Use expected scores, independent of the
host truth used to replay this fixture. Persist resulting oracle observation but do not
feed it into a second step. No outcome-based retries, action repairs, or fallback.
Use unchanged pilot1b_parser for base and revision responses. Invalid shared bases
invalidate the matched quartet; retain them in intention-to-run denominators. Invalid
final responses remain failures with missing cost/score, never zero-cost successes.
Report validity separately and both all-attempt and valid-execution rate denominators.
Transport failures stay recorded; any resumption must preserve seeds and requests.

## Runtime, seeds and call budget

Reuse Pilot 1b: local Ollama localhost:11435, gemma4e-64k:latest, parent gemma4:e4b
Q4_K_M, recorded Ollama 0.31.2/Vulkan Radeon 780M, 8 threads. Model blob digest:
sha256:4c27e0f5b5adf02ac956c7322bd2ee7636fe3f45a8512c9aba5385242cb6e09a.
Temperature .7, top_p 1, top_k 64, repeat_penalty 1, num_ctx 4096, think=false;
num_predict 256 base/selector, 512 revision. No structured-output mode. Runtime identity
must be verified read-only before an approved run; it has not been newly probed here.

Prespecify snapshot index i=0..9 and trial t=0..9: base seed 101+1000*i+t;
selector seed 100101+1000*i+t; revision seed 200101+1000*i+t. Distinct role ranges;
reuse revision seed across B/C/D for pairing. Seeds are not independent observations
across arms. Rotate B/C/D execution order by trial, without changing PF order. Persist
exact request payloads, raw responses, token counts, completion reason and call IDs.
Check actual rendered input length against context capacity before approved inference;
if oversized, stop for protocol review rather than silently truncate or raise context.

Primary: 100 shared base + 100 B selector + up to 100 B revision + 100 C revision +
100 D revision = 400–500 calls if bases validate (500 ceiling absent retries).
No model calls have been made for this checkpoint.

Only AFTER the main comparison is recorded/analyzed, optional B_reverse adds 100
selectors and up to 100 revisions using cached bases and the same paired role seeds.
Reverse rendered native PF-menu lines only; retain native tag-order dispatch. Canonical
native menu is alphabetical: binary_isolation, comparison_experiment, dependency_trace,
evidence_collection, request_id_trace. This differs from C's fixed intervention order.
Optional C_reverse adds 100 revisions, reversed eligible dispatch order, fresh counts,
same cached bases and revision seeds. Keep these sensitivity conditions separate.
Total ceiling including both sensitivities: 800 calls. Neither is authorized now.

## Recording and prespecified analysis

Per trial/arm retain snapshot/trial, public evidence, full menu/order, PF available,
raw selection, parsed selected list/order, independent gates for all five, actual
selected gates, activated IDs/records, exact intervention strings/order, counts before
and after, base/revision/executed text and action, and offline all-action scores/best.
Record eligible set, selected intersection eligible, selected minus eligible, eligible
minus selected, number eligible/selected/activated, dispatch order and executed-action
score minus base score. C retained IDs are experimental eligibility assignment, not
model-selected IDs; A/D selection metrics are not applicable. Empty B selection has
zero recall, undefined precision; report its frequency rather than assigning precision 1.

Primary diagnostic score is unchanged expected eliminations per cost. Optimal means
native evaluator rank==1; top-2 means rank<=2 (competition ranks with all boundary ties).
Report expected-optimal executed-action rate, top-2 rate, mean score, mean cost of
executed action, strict score improvement/degradation and unchanged-score/action-change
rates. Mean scores/costs use valid executions with failure counts alongside. Report D's
improvement/degradation explicitly and paired B-A, C-A, D-A, B-D and C-B differences.
Do not score PF selection as diagnostic success. Higher cost is not automatically worse:
report action transitions, especially cheap B/D versus generic C/E or replay F.

For B report per-PF selection/activation rates, eligible recall |S∩E|/|E|, precision
|S∩E|/|S| (both macro and micro, with empty-set handling), multi-selection |S|>=2,
multi-eligible selection |S∩E|>=2, and actual multi-activation. Cross-tab action quality
by number eligible (2 vs 3), eligible selected, activated and selected-but-ineligible.
Show omissions and false-gate selection frequencies separately. Associations of
multi-selection with quality are descriptive because native selection is endogenous.

Best-strategy alignment PRIMARY operationalization: final executed action belongs to
the exact offline best-action set. Also report broad action directions (A tracing,
B/D comparison, C exception inspection, E dependencies, F isolation). This direction
summary must not replace exact-action success: B and D often have different scores.
There is no unique native PF-to-action map: request_id_trace spans A/C; comparison
includes D/F; evidence_collection includes D. Consequently, the question of selecting
“the best PF” is only partially identifiable. Report exact selections alongside optimal
actions and actual intervention text; do not invent a best-PF oracle or add a selector.
An omitted eligible PF is not proven useful merely by its name; C-B improvement offers
bundle-level evidence, not individual-PF causality.

Report each snapshot first, then equal-snapshot means, paired trial distributions and
uncertainty with snapshots as clusters (only ten, structurally related); avoid treating
400 arm observations as independent. Show the three viable-world-set strata. With
10 seeds, differences are pilot evidence, not reliability or novelty claims.

For B_reverse report paired selected-set/order changes, activation changes, action
changes, score/cost differences and optimal-rate differences. For C_reverse report
paired final actions and scores. Never pool reversal runs into primary estimates.

Native high-value execution beyond both base and D would weaken selector motivation.
Relevant selection with weak execution, interference, omissions or weak value alignment
may motivate testing a comparative selector, but neither result establishes novelty.
This design cannot assess unresolved comparison/isolation competition or broad generality.

## Integrity and checkpoint stop

All sources pinned by Pilot 1b's manifest were checked byte-for-byte before and after
the offline audit, including PF implementation, native wrappers, selector, dispatcher,
policy adapter, parser, oracle, evaluator, actions, hypotheses and support documents.
No existing source was changed. audit.json stores the verified hashes. Only the new
offline builder and checkpoint artifacts were added. No live runner or selector was
implemented. Review this fixed evidence suite and protocol before any inference.
